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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* GLOBAL RESET & TYPOGRAPHY */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body, .stApp {
    background-color: #1a1b2e !important;
    color: #e6e9f2 !important;
    font-size: 14.5px;
    line-height: 1.6;
}

/* STREAMLIT CHROME REMOVAL */
header[data-testid="stHeader"], 
footer, 
#MainMenu, 
div[data-testid="stToolbar"] {
    display: none !important;
}

/* CUSTOM LINEAR SPINNER */
div[data-testid="stSpinner"] > div:first-child {
    display: none !important; /* Hide the circular SVG */
}
div[data-testid="stSpinner"] {
    position: relative;
    padding-top: 12px;
}
div[data-testid="stSpinner"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%;
    height: 3px;
    background: #1a1b2e;
    border-radius: 2px;
    overflow: hidden;
}
div[data-testid="stSpinner"]::after {
    content: '';
    position: absolute;
    top: 0; left: -50%;
    width: 50%;
    height: 3px;
    background: #7aa2f7;
    border-radius: 2px;
    animation: linear-progress 1.5s infinite ease-in-out;
}
@keyframes linear-progress {
    0% { left: -50%; }
    100% { left: 100%; }
}

/* SPACING REBUILD - ASYMMETRICAL LAYOUT */
section.main > div.block-container {
    padding: 4rem 5rem !important;
    max-width: 1400px;
    margin: 0 !important;
}

/* SIDEBAR REBUILD - DEEP FOCUS MODE */
section[data-testid="stSidebar"] {
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    background: rgba(34, 36, 54, 0.7) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid #30363d !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
    padding: 2.5rem 1.5rem !important;
}

/* SIDEBAR NAV ITEMS AND TEXT */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #66708f !important;
    margin-top: 2rem;
    margin-bottom: 0.75rem;
}

/* ZERO HEIGHT FOR MARKER CONTAINERS */
div.element-container:has(span[class^="marker-"]) {
    margin: 0 !important;
    padding: 0 !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden;
}

/* MARKER-BASED CONTAINER STYLING - MODULE BLOCKS */
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-module-active) {
    background: #222436;
    border-radius: 2px;
    border: 1px solid #30363d;
    padding: 32px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-module-active)::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 3px; height: 100%;
    background: #7aa2f7;
}

div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-module-completed) {
    background: #222436;
    border-radius: 2px;
    border: 1px solid #30363d;
    padding: 32px 40px;
    margin-bottom: 24px;
    opacity: 0.65;
    transition: all 0.3s ease;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-module-completed):hover {
    opacity: 1;
}

div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-module-skipped) {
    background: #222436;
    border-radius: 2px;
    border: 1px solid #30363d;
    padding: 32px 40px;
    margin-bottom: 24px;
    opacity: 0.65;
}

/* QUIZ CARD */
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-quiz-card) {
    background: #222436;
    border-radius: 2px;
    border: 1px solid #30363d;
    padding: 28px;
    margin-top: 16px;
}

/* QUESTION BLOCK */
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-question-block) {
    background: #1a1b2e;
    border-radius: 2px;
    border: 1px solid #30363d;
    padding: 24px;
    margin-bottom: 16px;
}

/* VIDEO CONTAINER */
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-video-container) {
    background: #000000;
    border-radius: 2px;
    border: 1px solid #30363d;
    overflow: hidden;
    padding: 20px;
}

/* NOTES PANEL */
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-notes-panel) {
    background: #222436;
    border-radius: 2px;
    border: 1px solid #30363d;
    padding: 28px;
    margin-bottom: 16px;
}

/* COMPONENT STYLES (HTML) */
.eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #66708f;
    margin-bottom: 16px;
}

.module-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}

.module-title-group {
    display: flex;
    align-items: center;
    gap: 16px;
}

.module-number-pill {
    background: #1a1b2e;
    color: #9aa3bf;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    padding: 6px 10px;
    border-radius: 2px;
    border: 1px solid #30363d;
}

.module-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 19px;
    font-weight: 600;
    color: #e6e9f2;
    margin: 0;
    letter-spacing: -0.01em;
}

.status-pill {
    border-radius: 2px;
    padding: 6px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-completed { background: rgba(158, 206, 106, 0.08); color: #9ece6a; border: 1px solid #30363d; }
.status-skipped { background: rgba(187, 154, 247, 0.08); color: #bb9af7; border: 1px solid #30363d; }
.status-active { background: rgba(122, 162, 247, 0.08); color: #7aa2f7; border: 1px solid #30363d; }

.callout-orange {
    background: #1a1b2e;
    border: 1px solid #30363d;
    border-left: 3px solid #e0af68;
    color: #9aa3bf;
    padding: 16px 20px;
    border-radius: 2px;
    font-size: 14px;
    margin-bottom: 24px;
}

.course-card {
    background: #222436;
    padding: 28px;
    border-radius: 2px;
    border: 1px solid #30363d;
    margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
    cursor: pointer;
    position: relative;
}
.course-card:hover {
    border-color: #7aa2f7;
    background: #1a1b2e;
}

/* TYPOGRAPHY OVERRIDES */
h1, h2, h3, h4, h5 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #e6e9f2 !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
}

p, div {
    color: #9aa3bf;
}

/* RADIO BUTTONS (QUIZ) */
div[data-testid="stRadio"] > div {
    gap: 12px;
}
div[data-testid="stRadio"] label {
    background: #222436;
    border: 1px solid #30363d;
    border-radius: 2px;
    padding: 14px 18px;
    transition: all 0.2s ease;
    cursor: pointer;
}
div[data-testid="stRadio"] label:hover {
    border-color: #7aa2f7;
    background: #1a1b2e;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    border-color: #7aa2f7;
    background: rgba(122, 162, 247, 0.05);
}

/* TEXT AREA (NOTES) */
div[data-testid="stTextArea"] textarea {
    background-color: #1a1b2e !important;
    border: 1px solid #30363d !important;
    color: #e6e9f2 !important;
    border-radius: 2px !important;
    font-size: 15px;
    padding: 16px;
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    transition: border-color 0.2s ease;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #7aa2f7 !important;
}

/* BUTTON STYLES */
div[data-testid="stButton"] button {
    background: #222436;
    color: #e6e9f2;
    border: 1px solid #30363d;
    border-radius: 2px;
    padding: 6px 16px;
    font-weight: 500;
    transition: all 0.15s ease;
}
div[data-testid="stButton"] button:hover {
    border-color: #7aa2f7;
    background: #1a1b2e;
}

/* Mark as watched button */
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-video-container) div[data-testid="stButton"] button {
    width: 100%;
    padding: 12px;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-video-container) div[data-testid="stButton"] button:disabled {
    background: #1a1b2e;
    color: #66708f;
    border: 1px solid #30363d;
    cursor: not-allowed;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-video-container) div[data-testid="stButton"] button:not(:disabled) {
    background: rgba(158, 206, 106, 0.1);
    color: #9ece6a;
    border: 1px solid #30363d;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-video-container) div[data-testid="stButton"] button:not(:disabled):hover {
    background: rgba(158, 206, 106, 0.15);
    border-color: #9ece6a;
}

/* Notes Save Button */
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-notes-panel) div[data-testid="stButton"] button {
    background: transparent;
    color: #9aa3bf;
    border: 1px solid #30363d;
    margin-top: 8px;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container:nth-child(1) span.marker-notes-panel) div[data-testid="stButton"] button:hover {
    color: #e6e9f2;
    border-color: #7aa2f7;
    background: #1a1b2e;
}

/* Flashcard Specific */
.flashcard-front {
    background: #222436;
    border: 1px solid #30363d;
    border-radius: 2px;
    padding: 24px;
    margin-bottom: 16px;
    color: #e6e9f2;
    font-weight: 500;
    font-size: 15px;
}
.flashcard-back {
    background: rgba(158, 206, 106, 0.05);
    border: 1px solid #30363d;
    border-left: 3px solid #9ece6a;
    border-radius: 2px;
    padding: 24px;
    margin-bottom: 24px;
    color: #e6e9f2;
    font-weight: 400;
    font-size: 15px;
}

/* CUSTOM PROGRESS BAR HTML */
.custom-progress-container {
    margin-top: 24px;
    margin-bottom: 16px;
}
.custom-progress-track {
    background: #1a1b2e;
    border-radius: 2px;
    height: 4px;
    width: 100%;
    overflow: hidden;
    border: 1px solid #30363d;
}
.custom-progress-fill {
    background: #7aa2f7;
    height: 100%;
    border-radius: 2px;
    transition: width 1s linear;
}
.custom-progress-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #66708f;
    margin-top: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Form override */
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
}

/* TABS REDESIGN - COMMAND CENTER STYLE */
div[data-testid="stTabs"] {
    margin-top: 32px;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 8px;
    background: #222436;
    padding: 6px;
    border-radius: 2px;
    border: 1px solid #30363d;
    display: inline-flex;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent;
    border: none !important;
    color: #66708f;
    font-weight: 500;
    font-size: 13px;
    padding: 8px 16px;
    border-radius: 2px;
    transition: all 0.2s ease;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #9aa3bf;
    background: rgba(255,255,255,0.03);
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: #1a1b2e !important;
    color: #e6e9f2 !important;
    border: 1px solid #30363d !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none;
}

/* Text Inputs & Selectboxes */
div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #1a1b2e !important;
    border: 1px solid #30363d !important;
    color: #e6e9f2 !important;
    border-radius: 2px !important;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
    border-color: #7aa2f7 !important;
}

/* Make block containers look anchored */
div.block-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
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
    st.markdown('<div class="eyebrow" style="margin-top: 16px;">🃏 Flashcards</div>', unsafe_allow_html=True)
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

    with st.container():
        st.markdown('<span class="marker-notes-panel" style="display:none;"></span>', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">📝 My Notes</div>', unsafe_allow_html=True)
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
                st.toast("Notes saved successfully.")
            else:
                st.error("Failed to save notes.")


# ─────────────────────────────────────────────────────────────────────────────
# MODULE BLOCK
# ─────────────────────────────────────────────────────────────────────────────

def render_module_block(idx: int, mod: dict, tab_prefix: str = ""):
    with st.container():
        # Add the marker based on state
        if mod["is_skipped"]:
            st.markdown('<span class="marker-module-skipped" style="display:none;"></span>', unsafe_allow_html=True)
            status_html = '<div class="status-pill status-skipped">Skipped</div>'
        elif mod["is_completed"]:
            st.markdown('<span class="marker-module-completed" style="display:none;"></span>', unsafe_allow_html=True)
            status_html = '<div class="status-pill status-completed">Completed</div>'
        else:
            st.markdown('<span class="marker-module-active" style="display:none;"></span>', unsafe_allow_html=True)
            status_html = '<div class="status-pill status-active">In Progress</div>'

        # Render Header via HTML
        header_html = f"""
        <div class="module-header">
            <div class="module-title-group">
                <div class="module-number-pill">{idx + 1:02d}</div>
                <h3 class="module-title">{mod['title']}</h3>
            </div>
            {status_html}
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        st.markdown(f"<div style='color: #9aa3bf; font-size: 15px; line-height: 1.6; margin-bottom: 24px; padding-right: 40px;'>{mod['description']}</div>", unsafe_allow_html=True)

        if mod["is_skipped"]:
            st.markdown('<div class="callout-orange">⚡ You demonstrated knowledge of this module — it has been marked as complete!</div>', unsafe_allow_html=True)
            render_notes_panel(mod, tab_prefix)

        elif mod["is_completed"]:
            col_left, col_right = st.columns([3, 1])
            with col_left:
                with st.expander("📝 Workspace Notes", expanded=True):
                    render_notes_panel(mod, tab_prefix)
            with col_right:
                with st.expander("⚙️ System Tutor", expanded=False):
                    st.markdown('<div class="eyebrow" style="margin-top: 16px;">System Tutor</div>', unsafe_allow_html=True)
                    fc_key = f"flashcards_{mod['id']}_{tab_prefix}"
                    if st.button("Initialize Tutor", key=f"gen_fc_{mod['id']}_{tab_prefix}"):
                        with st.spinner("Processing..."):
                            fc_res = api_get(f"/modules/{mod['id']}/flashcards")
                            if fc_res.status_code == 200:
                                st.session_state[fc_key] = fc_res.json()
                            else:
                                st.error(f"System generation failed: {fc_res.text}")
                    if fc_key in st.session_state:
                        render_flashcard_viewer(st.session_state[fc_key]["cards"])

        else:
            # Active module: show video + theater drawer
            col1, col2 = st.columns([3, 1])

            with col1:
                with st.container():
                    st.markdown('<span class="marker-video-container" style="display:none;"></span>', unsafe_allow_html=True)
                    st.markdown('<div class="eyebrow">▶ Module Video</div>', unsafe_allow_html=True)
                    
                    if mod["video_id"]:
                        st.video(f"https://www.youtube.com/watch?v={mod['video_id']}")
                        mod_id_str = str(mod["id"])
                        if mod_id_str not in st.session_state.watch_start_times:
                            st.session_state.watch_start_times[mod_id_str] = time.time()
                    else:
                        st.markdown('<div class="callout-orange">⚠️ No suitable video found for this module.</div>', unsafe_allow_html=True)

                    video_duration = mod.get("video_duration") or 600
                    elapsed = time.time() - st.session_state.watch_start_times.get(str(mod["id"]), time.time())
                    
                    if elapsed < video_duration:
                        remaining = int(video_duration - elapsed)
                        pct = min(100, (elapsed / video_duration) * 100)
                        
                        prog_html = f"""
                        <div class="custom-progress-container">
                            <div class="custom-progress-track">
                                <div class="custom-progress-fill" style="width: {pct}%"></div>
                            </div>
                            <div class="custom-progress-text">⏳ {remaining // 60}m {remaining % 60}s remaining</div>
                        </div>
                        """
                        st.markdown(prog_html, unsafe_allow_html=True)
                        
                        st.button(
                            "✓ Mark as Watched",
                            key=f"watch_{mod['id']}_{tab_prefix}",
                            disabled=True,
                            help="Watch the entire video to unlock.",
                        )
                    else:
                        if st.button("✓ Mark as Watched", key=f"watch_{mod['id']}_{tab_prefix}"):
                            w_res = api_post(f"/modules/{mod['id']}/complete")
                            if w_res.status_code == 200:
                                st.rerun()

            with col2:
                # Theater Drawer: Notes & Challenge
                with st.expander("📝 Workspace Notes", expanded=True):
                    render_notes_panel(mod, tab_prefix)
                    
                with st.expander("⚙️ System Challenge", expanded=False):
                    st.markdown('<span class="marker-quiz-card" style="display:none;"></span>', unsafe_allow_html=True)
                    st.markdown('<div class="eyebrow">Accelerate Path</div>', unsafe_allow_html=True)
                    st.markdown("<div style='font-size: 13px; color: #a9b1d6; margin-bottom: 16px;'>Demonstrate proficiency to bypass this module.</div>", unsafe_allow_html=True)

                    quiz_key = f"quiz_{mod['id']}"
                    if st.button("Build Assessment", key=f"btn_{mod['id']}_{tab_prefix}"):
                        check_res = api_get(f"/modules/{mod['id']}/has-transcript", public=True)
                        has_transcript = check_res.status_code == 200 and check_res.json().get("has_transcript")
                        if not has_transcript:
                            st.markdown('<div class="callout-orange">System warning: No transcript available. Using topic-based parameters.</div>', unsafe_allow_html=True)
                        with st.spinner("Processing..."):
                            q_res = api_post("/generate-quiz", params={"module_id": mod["id"]})
                            if q_res.status_code == 200:
                                st.session_state[quiz_key] = q_res.json()
                            else:
                                st.error(f"System generation failed: {q_res.text}")

                    if quiz_key in st.session_state:
                        quiz_data = st.session_state[quiz_key]
                        with st.form(key=f"form_{mod['id']}_{tab_prefix}"):
                            answers = []
                            for q_idx, q in enumerate(quiz_data["questions"]):
                                with st.container():
                                    st.markdown('<span class="marker-question-block" style="display:none;"></span>', unsafe_allow_html=True)
                                    st.markdown(f"<div style='font-weight: 600; margin-bottom: 8px;'>Q{q_idx+1}: {q['question']}</div>", unsafe_allow_html=True)
                                    ans = st.radio(
                                        "Options",
                                        options=q["options"],
                                        key=f"q_{mod['id']}_{q_idx}_{tab_prefix}",
                                        label_visibility="collapsed"
                                    )
                                    answers.append((ans, q["correct_answer_index"], q["options"], q.get("explanation", "")))

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
                                            st.success(f"⚡ System Override Approved. Score: {score}/5. Module Bypassed.")
                                            del st.session_state[quiz_key]
                                            st.rerun()
                                        else:
                                            st.error(f"🛑 Verification Failed. Score: {score}/5. Watch the video to complete.")
                                            for err in wrong_explanations:
                                                st.warning(f"💡 {err}")
                                            del st.session_state[quiz_key]
