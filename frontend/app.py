import streamlit as st
import requests
import ui_components as ui

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OpenPath — AI Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.inject_css()

BACKEND_URL = "http://127.0.0.1:8000"

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in {
    "token": None,
    "user_id": None,
    "username": None,
    "course_id": None,
    "watch_start_times": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────────────────────
# AUTH PAGES  (shown before login)
# ─────────────────────────────────────────────────────────────────────────────

def render_auth_page():
    st.markdown(
        "<h1 style='text-align:center;margin-top:40px;'>🎓 OpenPath</h1>"
        "<p style='text-align:center;color:#8b949e;font-size:18px;'>AI-powered learning. Any skill. At your pace.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col_l, col_c, col_r = st.columns([1, 1.6, 1])
    with col_c:
        login_tab, signup_tab = st.tabs(["🔑 Login", "📝 Sign Up"])

        # ── Login ────────────────────────────────────────────────────────────
        with login_tab:
            with st.form("login_form"):
                st.markdown("### Welcome back")
                email = st.text_input("Email", placeholder="you@example.com", key="login_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pw")
                submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        res = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json={"email": email, "password": password},
                        )
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.token = data["access_token"]
                            st.session_state.user_id = data["user_id"]
                            st.session_state.username = data["username"]
                            st.rerun()
                        else:
                            try:
                                err_data = res.json().get("detail", "Login failed.")
                                if isinstance(err_data, list):
                                    detail = " | ".join([f"{e.get('loc',[])[-1]}: {e.get('msg')}" for e in err_data])
                                else:
                                    detail = err_data
                            except Exception:
                                detail = f"Login failed (HTTP {res.status_code})."
                            st.error(f"❌ {detail}")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ Backend is not running at http://127.0.0.1:8000")

        # ── Sign Up ──────────────────────────────────────────────────────────
        with signup_tab:
            with st.form("signup_form"):
                st.markdown("### Create your account")
                username = st.text_input("Username", placeholder="learner42", key="reg_username")
                reg_email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
                reg_pw = st.text_input("Password", type="password", placeholder="At least 6 characters", key="reg_pw")
                reg_pw2 = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="reg_pw2")
                reg_submitted = st.form_submit_button("Create Account", use_container_width=True)

            if reg_submitted:
                if not username or not reg_email or not reg_pw:
                    st.error("Please fill in all fields.")
                elif reg_pw != reg_pw2:
                    st.error("Passwords do not match.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        res = requests.post(
                            f"{BACKEND_URL}/auth/register",
                            json={"username": username, "email": reg_email, "password": reg_pw},
                        )
                        if res.status_code == 201:
                            # Clear any stale session data before redirecting to login
                            for k in ["token", "user_id", "username", "course_id", "watch_start_times"]:
                                st.session_state[k] = None if k != "watch_start_times" else {}
                            
                            st.success(f"Account for **{username}** created successfully! 🎉")
                            st.info("Please click the **Login** tab above to sign in with your new credentials.")
                        else:
                            try:
                                err_data = res.json().get("detail", "Registration failed.")
                                if isinstance(err_data, list):
                                    # Handle FastAPI validation errors (422)
                                    detail = " | ".join([f"{e.get('loc',[])[-1]}: {e.get('msg')}" for e in err_data])
                                else:
                                    detail = err_data
                            except Exception:
                                detail = f"Registration failed (HTTP {res.status_code})."
                            st.error(f"❌ {detail}")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ Backend is not running at http://127.0.0.1:8000")


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR  (shown after login)
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["token", "user_id", "username", "course_id", "watch_start_times"]:
                st.session_state[k] = None if k != "watch_start_times" else {}
            st.rerun()

        st.markdown("---")
        st.header("📚 My Courses")

        try:
            courses_res = ui.api_get("/courses")
            if courses_res.status_code == 200:
                user_courses = courses_res.json()
                if user_courses:
                    course_options = {f"{c['skill_name']} (ID:{c['id']})": c["id"] for c in user_courses}
                    selected = st.selectbox(
                        "Load a course",
                        options=["-- Select --"] + list(course_options.keys()),
                        key="course_selectbox",
                    )
                    if selected != "-- Select --":
                        st.session_state.course_id = course_options[selected]
                else:
                    st.caption("No courses yet. Generate one below!")
        except Exception:
            pass

        st.markdown("---")
        st.header("✨ New Course")
        skill_input = st.text_input("Skill to Learn", placeholder="e.g., Welding, PCB Design")
        level_input = st.slider("Current Skill Level (/10)", 0, 10, 0)
        time_input = st.selectbox("Time Commitment", ["2 hours/week", "5 hours/week", "10 hours/week", "Full-time"])
        depth_input = st.selectbox(
            "Desired Depth",
            ["Crash Course (3 modules)", "Standard (5 modules)", "In-Depth (8 modules)", "Comprehensive (12 modules)"],
        )

        if st.button("🚀 Generate Course", use_container_width=True):
            if not skill_input:
                st.error("Please enter a skill.")
            else:
                with st.spinner("Curating syllabus & sourcing videos (10–20s)..."):
                    try:
                        res = ui.api_post(
                            "/generate-course",
                            params={"skill": skill_input, "level": level_input, "time": time_input, "depth": depth_input},
                        )
                        if res.status_code == 200:
                            st.session_state.course_id = res.json()["id"]
                            st.success("Course generated! 🎉")
                            st.rerun()
                        else:
                            st.error(f"Error: {res.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ Backend is not running.")


# ─────────────────────────────────────────────────────────────────────────────
# DISCOVER TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_discover_tab():
    st.header("🌍 Community Course Marketplace")
    st.markdown("Browse syllabi created by other learners. Enroll to add a private copy to your dashboard.")

    try:
        res = ui.api_get("/courses/public", public=True)
        if res.status_code != 200:
            st.error("Could not load marketplace.")
            return

        public_courses = res.json()
        if not public_courses:
            st.info("No public courses yet. Be the first! Go to your course and toggle visibility to Public.")
            return

        # Filter / Search
        search_q = st.text_input("🔍 Search marketplace", placeholder="e.g., Python, Welding, PCB...", key="discover_search")
        filtered = [c for c in public_courses if search_q.lower() in c["skill_name"].lower()] if search_q else public_courses

        st.markdown(f"**{len(filtered)} course(s) found**")
        cols = st.columns(2)

        for i, course in enumerate(filtered):
            with cols[i % 2]:
                st.markdown(
                    f'<div class="course-card">'
                    f'<h4 style="color:#58a6ff;margin:0 0 8px 0">📘 {course["skill_name"]}</h4>'
                    f'<p style="margin:0;color:#8b949e;font-size:13px;">'
                    f'👤 {course.get("owner_username","Unknown")} &nbsp;|&nbsp; '
                    f'📦 {course.get("module_count",0)} modules &nbsp;|&nbsp; '
                    f'⏱ {course["time_commitment"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                enroll_key = f"enroll_{course['id']}"
                if st.button(f"Enroll →", key=enroll_key, use_container_width=True):
                    with st.spinner("Adding to your dashboard..."):
                        enroll_res = ui.api_post(f"/courses/{course['id']}/enroll")
                        if enroll_res.status_code == 200:
                            new_course = enroll_res.json()
                            st.session_state.course_id = new_course["id"]
                            st.success(f"Enrolled in **{course['skill_name']}**! Loading course...")
                            st.rerun()
                        elif enroll_res.status_code == 400:
                            st.warning("You already own this course.")
                        else:
                            st.error(f"Enrollment failed: {enroll_res.text}")

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend is not running.")


# ─────────────────────────────────────────────────────────────────────────────
# MY COURSE VIEW
# ─────────────────────────────────────────────────────────────────────────────

def render_course_view():
    try:
        res = ui.api_get(f"/courses/{st.session_state.course_id}")
        if res.status_code == 401:
            st.warning("Session expired. Please log in again.")
            st.session_state.token = None
            st.rerun()
            return
        if res.status_code != 200:
            st.error("Could not load course.")
            return

        data = res.json()
        course = data["course"]
        modules = data["modules"]

        # Header
        col_title, col_vis = st.columns([3, 1])
        with col_title:
            st.header(f"📘 {course['skill_name']}")
        with col_vis:
            is_public = course.get("is_public", False)
            vis_label = "🌍 Public" if is_public else "🔒 Private"
            if st.button(f"{vis_label} — Toggle", key="toggle_vis", use_container_width=True):
                toggle_res = ui.api_patch(
                    f"/courses/{course['id']}/visibility",
                )
                # Use requests directly for query param
                r = requests.patch(
                    f"{BACKEND_URL}/courses/{course['id']}/visibility",
                    headers=ui.auth_headers(),
                    params={"make_public": not is_public},
                )
                if r.status_code == 200:
                    st.rerun()

        # Progress bar
        completed_count = len([m for m in modules if m["is_completed"]])
        st.progress(
            completed_count / max(len(modules), 1),
            text=f"Progress: {completed_count}/{len(modules)} Modules Completed",
        )

        # Tabs
        tab_current, tab_syllabus, tab_completed, tab_discover = st.tabs([
            "▶ Current Module", "📋 Syllabus", "✅ Completed", "🌍 Discover"
        ])

        with tab_current:
            current_mod = next((m for m in modules if not m["is_completed"] and not m["is_skipped"]), None)
            if current_mod:
                current_idx = modules.index(current_mod)
                ui.render_module_block(current_idx, current_mod, "t0")
            else:
                st.balloons()
                st.success("🎉 You've completed all modules for this course! Incredible work.")

        with tab_syllabus:
            st.subheader("Full Course Syllabus")
            for idx, mod in enumerate(modules):
                if not mod["is_completed"] and not mod["is_skipped"]:
                    ui.render_module_block(idx, mod, "t1")

        with tab_completed:
            completed_mods = [m for m in modules if m["is_completed"] or m["is_skipped"]]
            if completed_mods:
                for idx, mod in enumerate(modules):
                    if mod["is_completed"] or mod["is_skipped"]:
                        ui.render_module_block(idx, mod, "t2")
            else:
                st.info("Complete your first module to see it here.")

        with tab_discover:
            render_discover_tab()

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend is not running at http://127.0.0.1:8000")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────

if not st.session_state.token:
    render_auth_page()
else:
    render_sidebar()

    if st.session_state.course_id:
        render_course_view()
    else:
        # Landing / Home when logged in but no course selected
        st.title(f"Welcome back, {st.session_state.username}! 👋")
        st.markdown(
            "Use the **sidebar** to generate a new course or load an existing one.\n\n"
            "Or explore community courses below:"
        )
        st.markdown("---")
        render_discover_tab()
