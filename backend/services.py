import os
import functools
from google import genai
from google.genai import types
from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
import schemas
from datetime import datetime
import re


# ─────────────────────────────────────────────────────────────────────────────
# SYLLABUS GENERATION  (with LRU cache to avoid redundant Gemini calls)
# ─────────────────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=128)
def _cached_syllabus(skill: str, level: int, time: str, depth: str) -> str:
    """
    Inner function whose result is cached by (skill, level, time, depth).
    Returns the raw JSON string so it is picklable by lru_cache.
    Already normalises skill to lowercase for better cache hits.
    """
    depth_match = re.search(r'\((\d+) modules\)', depth)
    num_modules = int(depth_match.group(1)) if depth_match else 5

    prompt = f"""
    Create a highly detailed, structured learning syllabus for learning "{skill}".
    The user's current skill level is {level}/10.
    Their time commitment is {time}.
    Their desired learning depth is "{depth}".
    Break the skill down into EXACTLY {num_modules} sequential, highly specific, and interconnected modules.
    Do not give general 'Introduction' or 'Advanced' titles; focus on specific sub-topics they need in order.

    CRITICAL: For each module's search_query field, generate a concise, highly targeted YouTube search query.
    The search_query MUST include the skill name "{skill}" and specific sub-topic keywords from the module.
    Example good query: "python pip virtualenv setup tutorial"
    Example bad query: "how to set up tools for python" (too vague, misses specific keywords)

    Generate the response strictly as a JSON object matching the requested schema.
    """

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schemas.CourseCreate,
            temperature=0.7,
        ),
    )
    return response.text


def generate_syllabus(skill: str, level: int, time: str, depth: str = "Standard (5 modules)") -> schemas.CourseCreate:
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    depth_match = re.search(r'\((\d+) modules\)', depth)
    num_modules = int(depth_match.group(1)) if depth_match else 5

    try:
        raw_json = _cached_syllabus(skill.strip().lower(), level, time, depth)
        return schemas.CourseCreate.model_validate_json(raw_json)
    except Exception as e:
        print("Gemini API skipped/failed. Using fallback mock data:", e)
        mock_modules = [
            schemas.ModuleBase(title="Module 1: The Fundamentals", description=f"Core syntax and basic theory necessary to understand {skill}.", order_index=1, search_query=f"{skill} absolute beginners explained"),
            schemas.ModuleBase(title="Module 2: Practical Setup & Tooling", description="Setting up the environment and learning the basic tools of the trade.", order_index=2, search_query=f"how to structure projects and use tools for {skill}"),
            schemas.ModuleBase(title="Module 3: Core Concepts", description="Moving beyond basics into standard industry practices.", order_index=3, search_query=f"intermediate {skill} concepts and examples"),
            schemas.ModuleBase(title="Module 4: Advanced Scenarios & Troubleshooting", description="Handling edge cases, debugging, and advanced patterns.", order_index=4, search_query=f"advanced {skill} debugging and architecture"),
            schemas.ModuleBase(title="Module 5: Project & Real-World Application", description="Tying everything together by analyzing a complete project.", order_index=5, search_query=f"{skill} full project walkthrough"),
            schemas.ModuleBase(title="Module 6: Optimization & Performance", description="Making it fast and responsive.", order_index=6, search_query=f"{skill} optimization and performance tuning"),
            schemas.ModuleBase(title="Module 7: Security & Best Practices", description="Securing your implementation.", order_index=7, search_query=f"{skill} security best practices"),
            schemas.ModuleBase(title="Module 8: Ecosystem & Integrations", description="Connecting with other popular tools.", order_index=8, search_query=f"{skill} ecosystem and third-party integrations"),
            schemas.ModuleBase(title="Module 9: Enterprise Architecture", description="Scaling up to massive systems.", order_index=9, search_query=f"{skill} enterprise architecture and scale"),
            schemas.ModuleBase(title="Module 10: Future Trends", description="What's next in the industry.", order_index=10, search_query=f"future of {skill} emerging trends"),
            schemas.ModuleBase(title="Module 11: Community & Open Source", description="Contributing and sharing.", order_index=11, search_query=f"how to contribute to {skill} open source"),
            schemas.ModuleBase(title="Module 12: Expert Mastery", description="The pinnacle of the craft.", order_index=12, search_query=f"{skill} expert level masterclass"),
        ]
        return schemas.CourseCreate(
            skill_name=skill,
            start_level=level,
            time_commitment=time,
            modules=mock_modules[:num_modules],
        )


# ─────────────────────────────────────────────────────────────────────────────
# VIDEO SEARCH & RANKING
# ─────────────────────────────────────────────────────────────────────────────

# Trusted / high-quality educational channels get a ranking boost.
PRIORITY_CHANNELS: set[str] = {
    "fireship", "traversy media", "the coding train", "cs dojo",
    "tech with tim", "corey schafer", "sentdex", "programming with mosh",
    "the net ninja", "web dev simplified", "kevin powell", "developedbyed",
    "ben awad", "theo - t3.gg", "theo", "jack herrington", "james q quick",
    "codewithharry", "freecodecamp.org", "codecademy", "neetcode",
    "neetcodeio", "william fiset", "abdul bari", "jenny's lectures cs it",
    "apna college", "brocode", "bro code", "networkchuck", "arjancodes",
    "3blue1brown", "statquest with josh starmer", "two minute papers",
    "yannic kilcher", "andrej karpathy", "deeplearning.ai",
    "techworld with nana", "acloud guru", "kodekloud",
    "veritasium", "kurzgesagt", "numberphile", "computerphile",
    "khan academy", "mit opencourseware", "crashcourse",
    "the futur", "flux academy", "juxtopposed",
    "ali abdaal", "thomas frank",
    "mark rober", "stuff made here", "ben eater", "sebastian lague",
}

# Channel keywords that usually indicate low-quality lecture captures
_INSTITUTIONAL_KEYWORDS = {
    "institute", "university", "college", "school of", "dept of",
    "department of", "iit", "lectures", "nptel", "academy of",
    "centre for", "center for", "faculty of",
}

# Negative title patterns — reject clickbait, reactions, shorts, etc.
_NEGATIVE_TITLE_PATTERNS = re.compile(
    r'\b(reaction|reacting|react to|shorts|tiktok|meme|funny|prank|roast|'
    r'drama|rant|worst|cringe|gone wrong|day in the life|vlog|unboxing|haul|'
    r'challenge|try not to|you won\'t believe)\b',
    re.IGNORECASE,
)


def _has_non_latin(text: str) -> bool:
    """Return True if more than 30% of alphabetic chars are non-Latin."""
    alpha = [c for c in text if c.isalpha()]
    if not alpha:
        return False
    non_latin = sum(1 for c in alpha if ord(c) > 0x024F)
    return (non_latin / len(alpha)) > 0.30


def _extract_topic_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from a text, removing stop words and module prefixes."""
    text = re.sub(r'module\s*\d+\s*[:–—\-]\s*', '', text, flags=re.IGNORECASE)
    words = set(re.findall(r'[a-z0-9#+.]+', text.lower()))
    stop_words = {
        "how", "to", "for", "and", "with", "the", "a", "an", "in", "of", "on",
        "use", "what", "is", "are", "guide", "tutorial", "explained", "english",
        "learn", "learning", "understanding", "introduction", "intro", "basics",
        "beginner", "beginners", "using", "your", "this", "that", "from", "into",
        "about", "their", "more", "most", "will", "can", "get", "it", "by", "up",
        "be", "do", "has", "have", "or", "not", "but", "you", "they", "its",
        "module", "setting", "practical", "core", "advanced", "real", "world",
    }
    return words - stop_words


def _clean_module_title(title: str) -> str:
    """Strip module numbering prefix, e.g. 'Module 2: Practical Setup' -> 'Practical Setup'."""
    return re.sub(r'^module\s*\d+\s*[:–—\-]\s*', '', title, flags=re.IGNORECASE).strip()


def parse_time_ago(time_text):
    if not time_text:
        return 0
    text = time_text.lower()
    if "hour" in text: return 1
    if "day" in text: return 1
    if "week" in text: return 7
    if "month" in text: return 30
    if "year" in text:
        num = int(re.search(r'\d+', text).group() or 1)
        return num * 365
    return 365


def rank_video(video: dict, query: str, depth: str = "",
               module_title: str = "", module_description: str = "",
               skill_name: str = "") -> float:
    """
    Score a video for relevance.  Returns -100 for hard-rejected videos.
    """
    # ── Duration gate ──
    duration_str = str(video.get("duration", "0:00"))
    parts = duration_str.split(":")
    minutes = 0
    try:
        if len(parts) == 3:
            minutes = int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 2:
            minutes = int(parts[0])
    except ValueError:
        pass

    if minutes < 5:
        return -100.0
    max_duration = 120 if "In-Depth" in depth or "Comprehensive" in depth else 60
    if minutes > max_duration:
        return -100.0

    title = str(video.get("title", ""))

    # ── Language gate ──
    if _has_non_latin(title):
        return -100.0

    title_lower = title.lower()

    # ── Clickbait gate ──
    if _NEGATIVE_TITLE_PATTERNS.search(title_lower):
        return -100.0

    # ── Relevance (weight: 0.50) — strict gating ──
    query_keywords = _extract_topic_keywords(query)
    title_keywords = _extract_topic_keywords(module_title) if module_title else set()
    desc_keywords = _extract_topic_keywords(module_description) if module_description else set()
    skill_keywords = _extract_topic_keywords(skill_name) if skill_name else set()

    # All context keywords from our side
    all_context_keywords = query_keywords | title_keywords | desc_keywords | skill_keywords
    # Keywords extracted from the video title
    video_title_keywords = _extract_topic_keywords(title)

    if all_context_keywords:
        # Proper set intersection matching
        forward_matches = all_context_keywords.intersection(video_title_keywords)
        
        # Multi-word phrase matching
        phrase_bonus = 0.0
        if skill_name and skill_name.lower() in title_lower:
            phrase_bonus += 0.2
        if module_title and _clean_module_title(module_title).lower() in title_lower:
            phrase_bonus += 0.3
            
        forward_ratio = len(forward_matches) / len(all_context_keywords) if all_context_keywords else 0
        if forward_ratio < 0.15 and phrase_bonus < 0.3:
            return -100.0
            
        # Semantic skill anchoring penalty if missing
        if skill_keywords and not skill_keywords.intersection(video_title_keywords):
            phrase_bonus -= 0.15

        reverse_ratio = len(forward_matches) / len(video_title_keywords) if video_title_keywords else 0

        # Combined relevance
        relevance = min(1.0, (forward_ratio * 0.60) + (reverse_ratio * 0.40) + phrase_bonus)
    else:
        relevance = 1.0

    score = relevance * 0.50

    if relevance < 0.25:
        return -100.0

    # ── Educational intent detection ──
    educational_keywords = {"course", "tutorial", "guide", "lecture", "explained", "masterclass", "crash course", "fundamentals", "basics", "advanced", "learn"}
    if any(kw in title_lower for kw in educational_keywords):
        score += 0.10

    # ── Channel quality (weight: 0.15) ──
    channel_name = str(video.get("channel", "")).strip().lower()
    if channel_name in PRIORITY_CHANNELS:
        score += 1.0 * 0.15
    elif any(kw in channel_name for kw in _INSTITUTIONAL_KEYWORDS):
        score += 0.0
    else:
        score += 0.3 * 0.15

    # ── Views (weight: 0.15) ──
    views_str = video.get("views", "0")
    views_num = int("".join(filter(str.isdigit, str(views_str))) or 0)
    if views_num > 1_000_000: views_score = 1.0
    elif views_num > 100_000: views_score = 0.8
    elif views_num > 10_000: views_score = 0.5
    else: views_score = 0.1
    score += views_score * 0.15

    # ── Structure (weight: 0.05) ──
    desc = str(video.get("long_desc", ""))
    has_timestamps = bool(re.search(r'\d{1,2}:\d{2}', desc))
    structure_score = 1.0 if has_timestamps else (0.5 if len(desc) > 50 else 0)
    score += structure_score * 0.05

    # ── Recency (weight: 0.05) ──
    days_ago = parse_time_ago(video.get("publish_time", ""))
    if days_ago < 30: recency_score = 1.0
    elif days_ago < 365: recency_score = 0.7
    else: recency_score = max(0, 1.0 - (days_ago / 3650))
    score += recency_score * 0.05

    return score


def get_video_seconds(video: dict) -> int:
    """Parse video duration to seconds. Returns 600 (10-min watch-wall) on any failure."""
    duration_str = str(video.get("duration", ""))
    if not duration_str:
        return 600
    parts = duration_str.split(":")
    try:
        if len(parts) == 3:
            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            seconds = int(parts[0]) * 60 + int(parts[1])
        else:
            return 600
        return seconds if seconds > 0 else 600
    except (ValueError, IndexError):
        return 600


def _ai_rerank_videos(candidates: list[dict], module_title: str, module_description: str, skill_name: str) -> dict:
    """Use Gemini to pick the best educational video from a shortlist of highly relevant candidates."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
        
    client = genai.Client()
    
    candidates_json = []
    for i, v in enumerate(candidates):
        candidates_json.append({
            "index": i,
            "title": v.get("title", ""),
            "channel": v.get("channel", ""),
            "duration": v.get("duration", ""),
            "views": v.get("views", "0")
        })
        
    prompt = f"""
    You are an expert curriculum designer. We need the best educational YouTube video for a student learning "{skill_name}".
    
    Module Title: {module_title}
    Module Description: {module_description}
    
    Here is a shortlist of candidate videos (already filtered for basic relevance):
    {candidates_json}
    
    Select the single most educationally relevant video.
    Prefer exact subtopic matches, structured tutorials, educational channels, and strong curriculum alignment.
    Respond ONLY with a JSON object containing the chosen 'index' (integer).
    Example: {{"index": 2}}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            )
        )
        import json
        choice = json.loads(response.text)
        idx = choice.get("index", 0)
        if 0 <= idx < len(candidates):
            return candidates[idx]
    except Exception as e:
        print(f"[AI Rerank] Failed: {e}")
        
    # Fallback to the first candidate
    return candidates[0]

def find_best_video(query: str, exclude_ids: set = None, depth: str = "",
                    module_title: str = "", module_description: str = "",
                    skill_name: str = "") -> dict:
    """Search YouTube and return the best-matching video using diversified search and AI reranking."""
    exclude_ids = exclude_ids or set()
    max_res = 20 if "Comprehensive" in depth or "In-Depth" in depth else 15

    clean_title = _clean_module_title(module_title) if module_title else ""

    # Diversified search strategies
    search_strategies = [
        query, # 1. Exact module query search
    ]
    if clean_title and skill_name:
        search_strategies.append(f"{skill_name} {clean_title} tutorial") # 2. Skill + subtopic search
    if clean_title:
        search_strategies.append(f"{clean_title} explained {skill_name}") # 3. Explainer-style search
    
    # 4. Description-derived search
    if module_description:
        desc_keywords = list(_extract_topic_keywords(module_description))[:3]
        if desc_keywords:
            search_strategies.append(f"{skill_name} {clean_title} {' '.join(desc_keywords)}")
            
    # 5. Broad fallback search
    search_strategies.append(f"{skill_name} tutorial")

    from youtube_search import YoutubeSearch

    all_candidates = []

    for strategy_idx, search_query in enumerate(search_strategies):
        try:
            results = YoutubeSearch(search_query, max_results=max_res).to_dict()
            if not results:
                continue
            if exclude_ids:
                results = [v for v in results if v.get("id") not in exclude_ids]
            if not results:
                continue

            scored = [
                (v, rank_video(v, query, depth, module_title, module_description, skill_name))
                for v in results
            ]
            valid = [(v, s) for v, s in scored if s > -20]
            
            for v, s in valid:
                all_candidates.append({"video": v, "score": s})
                
            # Early exit if we found exceptionally good matches
            if any(s > 0.8 for _, s in valid):
                break

        except Exception as e:
            print(f"YouTube search failed for strategy {strategy_idx} query '{search_query}': {e}.")
            continue

    if not all_candidates:
        print(f"  [video] ALL strategies exhausted for module '{module_title}' — no video found.")
        return None

    # Deduplicate candidates
    unique_candidates = {}
    for item in all_candidates:
        vid_id = item["video"].get("id")
        if vid_id not in unique_candidates or unique_candidates[vid_id]["score"] < item["score"]:
            unique_candidates[vid_id] = item
            
    # Sort by score descending
    sorted_candidates = sorted(unique_candidates.values(), key=lambda x: x["score"], reverse=True)
    
    # Take top 5 candidates for AI reranking
    top_candidates = [item["video"] for item in sorted_candidates[:5]]
    top_score = sorted_candidates[0]["score"]
    runner_up_score = sorted_candidates[1]["score"] if len(sorted_candidates) > 1 else 0.0

    if len(top_candidates) > 1 and (top_score - runner_up_score) < 0.10:
        best_video = _ai_rerank_videos(top_candidates, module_title, module_description, skill_name)
    else:
        best_video = sorted_candidates[0]["video"]
    
    if best_video:
        duration = get_video_seconds(best_video)
        channel = best_video.get("channel", "?")
        print(f"  [video] AI selected -> [{channel}] {best_video.get('title', '?')[:60]}")
        return {"id": best_video.get("id"), "duration": duration}

    return None


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_quiz_from_transcript(video_id: str, module_id: int, fallback_topic: str = "") -> schemas.Quiz:
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry["text"] for entry in transcript])[:15000]

        client = genai.Client()
        prompt = (
            f"Read the following video transcript and generate exactly 5 multiple choice questions. "
            f"The questions must test comprehension of the material.\nTranscript: {transcript_text}"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schemas.Quiz,
                temperature=0.3,
            ),
        )
        quiz_data = schemas.Quiz.model_validate_json(response.text)
        quiz_data.module_id = module_id
        return quiz_data

    except Exception as e:
        print(f"[Quiz] Transcript fetch failed for '{video_id}': {e}. Falling back to topic-based quiz.")
        try:
            client = genai.Client()
            topic_prompt = (
                f'Generate exactly 5 multiple choice questions that test solid conceptual understanding of: "{fallback_topic}". '
                "Focus on specific concepts, trade-offs, best practices, or pitfalls. "
                "DO NOT use True/False questions or 'All of the above'/'None of the above' options."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=topic_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schemas.Quiz,
                    temperature=0.3,
                ),
            )
            quiz_data = schemas.Quiz.model_validate_json(response.text)
            quiz_data.module_id = module_id
            return quiz_data
        except Exception as fallback_e:
            print(f"[Quiz] Topic-based fallback also failed: {fallback_e}. Serving mock quiz.")
            topic_str = fallback_topic if fallback_topic else "the fundamentals"
            return schemas.Quiz(
                module_id=module_id,
                questions=[
                    schemas.QuizQuestion(question=f"Which of the following is a core concept regarding {topic_str}?", options=["Irrelevant Metric", "The specific concept explained in the material", "Historical Anecdote", "Hardware Specifications"], correct_answer_index=1, explanation="This is the central theme of the module."),
                    schemas.QuizQuestion(question="What common mistake do beginners make?", options=["Overthinking the architecture", "Skipping the fundamentals", "Using outdated tooling", "Ignoring documentation"], correct_answer_index=1, explanation="Skipping fundamentals is the most common pitfall."),
                    schemas.QuizQuestion(question=f"Which tool/approach is heavily emphasized for {topic_str}?", options=["Local Scripts", "Standardized Industry Best Practices", "Manual Implementation", "Deprecated Frameworks"], correct_answer_index=1, explanation="Standardization ensures reproducibility."),
                    schemas.QuizQuestion(question="True or False: The concepts learned here apply only to small-scale projects.", options=["True", "False", "Partially True", "Depends on context"], correct_answer_index=1, explanation="These concepts scale natively."),
                    schemas.QuizQuestion(question="What is the recommended next step after mastering this module?", options=["Stop learning", "Move on to advanced edge cases", "Switch fields entirely", "Repeat from Module 1"], correct_answer_index=1, explanation="The module structurally leads into advanced cases."),
                ],
            )


# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_flashcards(module_id: int, video_id: str | None, fallback_topic: str = "") -> schemas.FlashcardSet:
    """Generate 3-5 AI flashcards for a completed module using transcript or topic."""
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    context = ""
    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            context = " ".join([entry["text"] for entry in transcript])[:10000]
        except Exception:
            context = ""

    client = genai.Client()

    if context:
        prompt = (
            f"Based on this video transcript, generate 3 to 5 concise flashcards to help the learner remember key concepts.\n"
            f"Each flashcard should have a clear question (front) and a succinct answer (back).\n"
            f"Transcript: {context}"
        )
    else:
        prompt = (
            f'Generate 3 to 5 concise flashcards covering the most important concepts of: "{fallback_topic}".\n'
            "Each flashcard: front = specific question or term, back = clear, concise answer or definition."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schemas.FlashcardSet,
                temperature=0.4,
            ),
        )
        card_set = schemas.FlashcardSet.model_validate_json(response.text)
        card_set.module_id = module_id
        return card_set
    except Exception as e:
        print(f"[Flashcards] Gemini failed: {e}. Returning mock flashcards.")
        return schemas.FlashcardSet(
            module_id=module_id,
            cards=[
                schemas.Flashcard(front=f"What is the primary goal of {fallback_topic}?", back="To provide a structured foundation for the skill being learned."),
                schemas.Flashcard(front="What is the most common pitfall beginners face?", back="Skipping foundational concepts and jumping straight to advanced material."),
                schemas.Flashcard(front="What approach is recommended for mastering this module?", back="Practice consistently, review examples, and apply the concepts in small projects."),
            ],
        )

# ─────────────────────────────────────────────────────────────────────────────
# LIVE TUTOR CHAT
# ─────────────────────────────────────────────────────────────────────────────

def chat_with_module(video_id: str, module_topic: str, messages: list[schemas.ChatMessage]) -> str:
    """Chat with the context of a specific module."""
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    context = ""
    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            context = " ".join([entry["text"] for entry in transcript])[:15000]
        except Exception:
            context = ""
    
    client = genai.Client()
    
    # Build prompt
    history = "\n".join([f"{msg.role}: {msg.content}" for msg in messages[:-1]])
    user_query = messages[-1].content if messages else ""
    
    prompt = f"""
    You are an expert AI tutor helping a student learn about: "{module_topic}".
    Here is the transcript of the video they are watching:
    {context}
    
    Conversation History:
    {history}
    
    User: {user_query}
    
    Provide a helpful, educational, and engaging response based primarily on the transcript if relevant.
    Use clear markdown formatting, with code blocks if needed. Keep it concise but comprehensive.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[Chat] Gemini failed: {e}")
        return "I'm having trouble connecting right now. Please try again later."


# ─────────────────────────────────────────────────────────────────────────────
# OFFLINE STUDY GUIDE
# ─────────────────────────────────────────────────────────────────────────────

def generate_offline_notes(video_id: str, module_topic: str) -> str:
    """Generate comprehensive offline markdown notes from a transcript."""
    if not os.environ.get("GEMINI_API_KEY"):
        return "# Error\nGEMINI API key not set."

    context = ""
    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            context = " ".join([entry["text"] for entry in transcript])[:15000]
        except Exception:
            context = ""
            
    client = genai.Client()
    
    prompt = f"""
    Create a highly structured, comprehensive offline study guide for: "{module_topic}".
    Here is the video transcript to base it on:
    {context}
    
    Distill this into concise Markdown notes. Include:
    - Key definitions
    - Core concepts
    - Code snippets or formulas if applicable
    - Summary
    - Revision bullets
    
    Make it visually appealing in Markdown format.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[Offline Notes] Gemini failed: {e}")
        return "# Error\nFailed to generate notes."


# ─────────────────────────────────────────────────────────────────────────────
# JOB READY CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

def calculate_job_readiness(job_title: str, company: str, user_completed_skills: list[str]) -> schemas.JobReadyResponse:
    """Calculate job readiness percentage and missing skills using Gemini."""
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
    client = genai.Client()
    
    prompt = f"""
    You are an expert career counselor and tech recruiter. 
    Analyze the job role: "{job_title}" at "{company}".
    
    The user has completed courses covering these skills: {', '.join(user_completed_skills) if user_completed_skills else 'None yet'}.
    
    Determine how ready they are for this role.
    Generate a JSON response matching the required schema:
    - readiness_percentage (int 0-100)
    - missing_skills (list of strings)
    - suggested_modules (list of strings)
    - roadmap (list of strings): Provide a clear, step-by-step list of specific skills or course titles the user needs to learn next. Make these highly specific and actionable (e.g., 'Learn Python Data Structures' instead of 'Get better at programming'). These roadmap items will be used directly to generate new courses.
    - estimated_time (string, e.g. "3 months")
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schemas.JobReadyResponse,
                temperature=0.3,
            )
        )
        return schemas.JobReadyResponse.model_validate_json(response.text)
    except Exception as e:
        print(f"[Job Ready] Gemini failed: {e}")
        return schemas.JobReadyResponse(
            readiness_percentage=10,
            missing_skills=["Everything"],
            suggested_modules=["Intro to Everything"],
            roadmap=["Start learning"],
            estimated_time="1 year"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SKILL GRAPH
# ─────────────────────────────────────────────────────────────────────────────

def generate_skill_graph(user_completed_skills: list[str]) -> schemas.SkillGraphResponse:
    """Generate a skill graph mapping dependencies and nodes for visualization."""
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
    client = genai.Client()
    
    prompt = f"""
    You are an expert curriculum designer. The user has completed courses on the following skills:
    {', '.join(user_completed_skills) if user_completed_skills else 'None'}
    
    Create an interconnected skill graph around these skills, expanding to related prerequisite and advanced skills.
    Return a list of nodes and links.
    - Each node should have: id (string), name (string), val (int, size/glow), completed (bool).
    - Each link should have: source (node id), target (node id).
    
    Generate JSON matching the schema for SkillGraphResponse.
    Make sure to include around 10-15 related skills.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schemas.SkillGraphResponse,
                temperature=0.3,
            )
        )
        return schemas.SkillGraphResponse.model_validate_json(response.text)
    except Exception as e:
        print(f"[Skill Graph] Gemini failed: {e}")
        return schemas.SkillGraphResponse(nodes=[], links=[])
