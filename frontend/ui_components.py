"""
ui_components.py — Reusable Streamlit UI components for OpenPath.
All styling constants and module rendering logic live here.
"""
import streamlit as st
import requests
import time

BACKEND_URL = "http://127.0.0.1:8000"

# ─────────────────────────────────────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp { background-color: #0d1117; color: #c9d1d9; }

div[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d;
}

.module-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    padding: 24px;
    border-radius: 12px;
    border: 1px solid #30363d;
    margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    transition: border-color 0.2s ease;
}
.module-card:hover { border-color: #58a6ff55; }

.course-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #30363d;
    margin-bottom: 16px;
    transition: border-color 0.2s ease, transform 0.15s ease;
}
.course-card:hover { border-color: #3fb950; transform: translateY(-2px); }

.flashcard-front {
    background: linear-gradient(135deg, #1f3a5f 0%, #1a2d4a 100%);
    border: 1px solid #58a6ff44;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
    font-weight: 600;
    color: #58a6ff;
}
.flashcard-back {
    background: linear-gradient(135deg, #1a3a2a 0%, #162d20 100%);
    border: 1px solid #3fb95044;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    color: #3fb950;
}

.badge-completed {
    background: #1a3a2a;
    color: #3fb950;
    border: 1px solid #3fb950;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
}
.badge-skipped {
    background: #1f3a5f;
    color: #58a6ff;
    border: 1px solid #58a6ff;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
}
.badge-locked {
    background: #3a2a1a;
    color: #d29922;
    border: 1px solid #d29922;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
}

h1, h2, h3 { color: #58a6ff !important; }

.stButton>button {
    background-color: #238636;
    color: white;
    border: 1px solid rgba(240,246,252,0.1);
    border-radius: 8px;
    font-weight: 500;
    transition: 0.2s all;
}
.stButton>button:hover {
    background-color: #2ea043;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(46,160,67,0.3);
}

.stTextInput>div>div>input, .stTextArea textarea {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border-bottom: 2px solid transparent;
    color: #8b949e;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    border-bottom-color: #58a6ff !important;
    color: #58a6ff !important;
}

div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #238636, #58a6ff) !important;
    border-radius: 4px;
}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def auth_headers() -> dict:
    """Return JWT Authorization header dict from session state."""
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"}


def api_get(path: str, params: dict = None, public: bool = False) -> requests.Response:
    headers = {} if public else auth_headers()
    return requests.get(f"{BACKEND_URL}{path}", headers=headers, params=params or {})


def api_post(path: str, params: dict = None, json: dict = None, public: bool = False) -> requests.Response:
    headers = {} if public else auth_headers()
    return requests.post(f"{BACKEND_URL}{path}", headers=headers, params=params or {}, json=json)


def api_patch(path: str, json: dict = None) -> requests.Response:
    return requests.patch(f"{BACKEND_URL}{path}", headers=auth_headers(), json=json or {})


# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD VIEWER
# ─────────────────────────────────────────────────────────────────────────────

def render_flashcard_viewer(cards: list):
    """Render a list of flashcards with a flip-style reveal."""
    st.markdown("#### 🃏 Flashcards")
    st.caption("Click 'Reveal Answer' to flip each card.")
    for i, card in enumerate(cards):
        st.markdown(f'<div class="flashcard-front">❓ {card["front"]}</div>', unsafe_allow_html=True)
        flip_key = f"flip_{i}_{card['front'][:20]}"
        if st.button(f"Reveal Answer #{i+1}", key=f"flip_btn_{i}_{card['front'][:10]}"):
            st.session_state[flip_key] = True
        if st.session_state.get(flip_key):
            st.markdown(f'<div class="flashcard-back">✅ {card["back"]}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# NOTES PANEL
# ─────────────────────────────────────────────────────────────────────────────

def render_notes_panel(mod: dict, tab_prefix: str):
    """Render a notes text area with a save button for a module."""
    notes_key = f"notes_text_{mod['id']}_{tab_prefix}"
    current_notes = mod.get("notes") or ""

    if notes_key not in st.session_state:
        st.session_state[notes_key] = current_notes

    st.markdown("#### 📝 My Notes")
    notes_val = st.text_area(
        "Jot down your key takeaways:",
        value=st.session_state[notes_key],
        key=f"notes_area_{mod['id']}_{tab_prefix}",
        height=120,
        label_visibility="collapsed",
        placeholder="What did you learn? Any important concepts to remember?",
    )

    if st.button("💾 Save Notes", key=f"save_notes_{mod['id']}_{tab_prefix}"):
        res = api_patch(f"/modules/{mod['id']}/notes", json={"notes": notes_val})
        if res.status_code == 200:
            st.session_state[notes_key] = notes_val
            st.success("Notes saved!", icon="✅")
        else:
            st.error("Failed to save notes.")


# ─────────────────────────────────────────────────────────────────────────────
# MODULE BLOCK
# ─────────────────────────────────────────────────────────────────────────────

def render_module_block(idx: int, mod: dict, tab_prefix: str = ""):
    with st.container():
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.subheader(f"Module {idx + 1}: {mod['title']}")
        st.write(mod["description"])

        if mod["is_skipped"]:
            st.markdown('<span class="badge-skipped">⚡ Skipped via Quiz</span>', unsafe_allow_html=True)
            st.success("You demonstrated knowledge of this module — it's been marked as complete!")
            # Show notes for skipped modules too
            st.markdown("---")
            render_notes_panel(mod, tab_prefix)

        elif mod["is_completed"]:
            st.markdown('<span class="badge-completed">✅ Completed</span>', unsafe_allow_html=True)
            st.markdown("---")

            # Notes & Flashcards for completed modules
            col_left, col_right = st.columns(2)
            with col_left:
                render_notes_panel(mod, tab_prefix)
            with col_right:
                st.markdown("#### 🃏 Flashcards")
                fc_key = f"flashcards_{mod['id']}_{tab_prefix}"
                if st.button("Generate Flashcards", key=f"gen_fc_{mod['id']}_{tab_prefix}"):
                    with st.spinner("Generating flashcards with Gemini..."):
                        fc_res = api_get(f"/modules/{mod['id']}/flashcards")
                        if fc_res.status_code == 200:
                            st.session_state[fc_key] = fc_res.json()
                        else:
                            st.error(f"Flashcard generation failed: {fc_res.text}")
                if fc_key in st.session_state:
                    render_flashcard_viewer(st.session_state[fc_key]["cards"])

        else:
            # Active module: show video + quiz
            st.markdown('<span class="badge-locked">▶ In Progress</span>', unsafe_allow_html=True)
            st.markdown("")
            col1, col2 = st.columns([2, 1])

            with col1:
                if mod["video_id"]:
                    st.video(f"https://www.youtube.com/watch?v={mod['video_id']}")
                    mod_id_str = str(mod["id"])
                    if mod_id_str not in st.session_state.watch_start_times:
                        st.session_state.watch_start_times[mod_id_str] = time.time()
                else:
                    st.warning("⚠️ No suitable video found for this module.")

                st.markdown("<br>", unsafe_allow_html=True)

                video_duration = mod.get("video_duration") or 600
                elapsed = time.time() - st.session_state.watch_start_times.get(str(mod["id"]), time.time())

                if elapsed < video_duration:
                    remaining = int(video_duration - elapsed)
                    st.button(
                        "✓ Mark as Watched",
                        key=f"watch_{mod['id']}_{tab_prefix}",
                        disabled=True,
                        help="Watch the entire video to unlock.",
                    )
                    st.warning(f"⏳ {remaining // 60}m {remaining % 60}s remaining to unlock completion.")
                else:
                    if st.button("✓ Mark as Watched", key=f"watch_{mod['id']}_{tab_prefix}"):
                        w_res = api_post(f"/modules/{mod['id']}/complete")
                        if w_res.status_code == 200:
                            st.rerun()

            with col2:
                # Quiz-to-Skip
                st.markdown("### ⚡ Accelerate")
                st.info("Already know this? Take a 5-question exam to skip this module.")

                quiz_key = f"quiz_{mod['id']}"
                if st.button("Generate Skip Quiz", key=f"btn_{mod['id']}_{tab_prefix}"):
                    check_res = api_get(f"/modules/{mod['id']}/has-transcript", public=True)
                    has_transcript = check_res.status_code == 200 and check_res.json().get("has_transcript")
                    if not has_transcript:
                        st.info("No transcript — generating a topic-based quiz instead.")
                    with st.spinner("Generating quiz..."):
                        q_res = api_post("/generate-quiz", params={"module_id": mod["id"]})
                        if q_res.status_code == 200:
                            st.session_state[quiz_key] = q_res.json()
                        else:
                            st.error(f"Quiz generation failed: {q_res.text}")

                if quiz_key in st.session_state:
                    quiz_data = st.session_state[quiz_key]
                    with st.form(key=f"form_{mod['id']}_{tab_prefix}"):
                        answers = []
                        for q_idx, q in enumerate(quiz_data["questions"]):
                            st.write(f"**Q{q_idx+1}: {q['question']}**")
                            ans = st.radio(
                                "Options",
                                options=q["options"],
                                key=f"q_{mod['id']}_{q_idx}_{tab_prefix}",
                            )
                            answers.append((ans, q["correct_answer_index"], q["options"], q.get("explanation", "")))
                            st.markdown("---")

                        if st.form_submit_button("Submit Answers"):
                            score = 0
                            wrong_explanations = []
                            for ans, correct_idx, options, expl in answers:
                                if ans == options[correct_idx]:
                                    score += 1
                                else:
                                    wrong_explanations.append(expl)

                            with st.spinner("Grading..."):
                                s_res = api_post("/submit-quiz", params={"module_id": mod["id"], "score": score})
                                if s_res.status_code == 200:
                                    res_data = s_res.json()
                                    if res_data["passed"]:
                                        st.success(f"🎉 Passed! Score: {score}/5. Module Skipped!")
                                        del st.session_state[quiz_key]
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed. Score: {score}/5. Watch the video to complete.")
                                        for err in wrong_explanations:
                                            st.warning(f"💡 {err}")
                                        del st.session_state[quiz_key]

        st.markdown("</div>", unsafe_allow_html=True)
