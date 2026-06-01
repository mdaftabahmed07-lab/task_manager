"""
api_client.py — Shared HTTP client for the Task Manager Streamlit app.
All pages import from here so the base URL and token logic live in one place.
"""

import streamlit as st
import requests
from datetime import datetime

# ── Default API base (can be overridden in session_state) ─────────────────
DEFAULT_BASE_URL = "https://taskmanager-production-31ba.up.railway.app"


def get_base_url() -> str:
    return st.session_state.get("base_url", DEFAULT_BASE_URL).rstrip("/")


def auth_headers() -> dict:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


# ── Generic request helpers ────────────────────────────────────────────────

def _request(method: str, path: str, *, use_auth: bool = True, **kwargs):
    headers = auth_headers() if use_auth else {}
    try:
        return requests.request(
            method,
            f"{get_base_url()}{path}",
            headers=headers,
            timeout=10,
            **kwargs,
        )
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot reach the API. Is your FastAPI server running?")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out.")
        return None


def api_get(path: str, params: dict | None = None):
    return _request("GET", path, params=params)


def api_post(path: str, json: dict | None = None, use_auth: bool = True):
    return _request("POST", path, use_auth=use_auth, json=json)


def api_put(path: str, json: dict | None = None):
    return _request("PUT", path, json=json)


def api_delete(path: str):
    return _request("DELETE", path)


# ── Task helpers ───────────────────────────────────────────────────────────

def load_tasks(
    status: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 100,
) -> dict:
    params: dict = {"page": page, "page_size": page_size}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if search:
        params["search"] = search
    r = api_get("/tasks", params=params)
    if r and r.status_code == 200:
        return r.json()
    return {"total": 0, "page": 1, "page_size": page_size, "results": []}


# ── Formatting helpers ─────────────────────────────────────────────────────

PRIORITY_COLOR = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
STATUS_COLOR   = {"todo": "#0284c7", "in_progress": "#d97706", "done": "#16a34a"}


def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return iso


def status_badge(status: str) -> str:
    label = status.replace("_", " ").title()
    return f'<span class="badge badge-{status}">{label}</span>'


def priority_badge(priority: str) -> str:
    return f'<span class="badge badge-{priority}">{priority.title()}</span>'


# ── Shared CSS injected by every page ─────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 1.8rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.8rem;
    color: white;
}
.main-header h1 { font-family: 'Space Mono', monospace; font-size: 1.8rem; margin: 0; letter-spacing:-1px; }
.main-header p  { margin: 0.3rem 0 0; opacity: 0.7; font-size: 0.9rem; }
.user-pill {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 999px;
    padding: 3px 14px;
    font-size: 0.82rem;
    display: inline-block;
    margin-top: 0.5rem;
    color: white;
}

.task-card {
    background: white;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.9rem;
    border-left: 5px solid #ccc;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow .2s;
}
.task-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
.task-card.high   { border-color: #ef4444; }
.task-card.medium { border-color: #f59e0b; }
.task-card.low    { border-color: #22c55e; }
.task-title { font-weight: 600; font-size: 1rem; margin-bottom: 0.25rem; }
.task-desc  { color: #666; font-size: 0.88rem; margin-bottom: 0.55rem; }
.task-meta  { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }

.badge { display:inline-block; padding:2px 10px; border-radius:999px;
         font-size:0.76rem; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }
.badge-todo        { background:#e0f2fe; color:#0284c7; }
.badge-in_progress { background:#fef3c7; color:#d97706; }
.badge-done        { background:#dcfce7; color:#16a34a; }
.badge-high        { background:#fee2e2; color:#dc2626; }
.badge-medium      { background:#fef9c3; color:#ca8a04; }
.badge-low         { background:#f0fdf4; color:#16a34a; }

.stat-card { background:white; border-radius:12px; padding:1.1rem;
             text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.stat-num   { font-family:'Space Mono',monospace; font-size:1.9rem; font-weight:700; }
.stat-label { font-size:0.82rem; color:#666; margin-top:.15rem; }

#MainMenu, footer { visibility:hidden; }
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    user_name = (st.session_state.get("user") or {}).get("full_name", "")
    pill = f'<span class="user-pill">👤 {user_name}</span>' if user_name else ""
    st.markdown(
        f"""<div class="main-header">
                <h1>{title}</h1>
                {"" if not subtitle else f"<p>{subtitle}</p>"}
                {pill}
            </div>""",
        unsafe_allow_html=True,
    )


# ── Sidebar login / register widget ───────────────────────────────────────

def sidebar_auth():
    """Render sidebar: API URL input + login/register. Returns True if logged in."""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        base = st.text_input(
            "API Base URL",
            value=st.session_state.get("base_url", DEFAULT_BASE_URL),
            key="base_url_input",
        )
        st.session_state["base_url"] = base
        st.markdown("---")

        if st.session_state.get("token"):
            user = st.session_state.get("user") or {}
            st.success(f"✅ **{user.get('full_name', 'User')}**")
            st.caption(user.get("email", ""))
            if st.button("🚪 Logout", use_container_width=True):
                for k in ("token", "user"):
                    st.session_state.pop(k, None)
                st.rerun()
            return True
        else:
            st.markdown("### 🔐 Account")
            tab_login, tab_reg = st.tabs(["Login", "Register"])

            with tab_login:
                with st.form("login_form"):
                    email    = st.text_input("Email", key="li_email")
                    password = st.text_input("Password", type="password", key="li_pass")
                    if st.form_submit_button("Login", use_container_width=True):
                        r = api_post("/auth/login", {"email": email, "password": password}, use_auth=False)
                        if r and r.status_code == 200:
                            d = r.json()
                            st.session_state["token"] = d["access_token"]
                            st.session_state["user"]  = d["user"]
                            st.rerun()
                        elif r:
                            st.error(r.json().get("detail", "Login failed"))

            with tab_reg:
                with st.form("reg_form"):
                    full_name = st.text_input("Full Name", key="rg_name")
                    email_r   = st.text_input("Email", key="rg_email")
                    pass_r    = st.text_input("Password (min 8 chars)", type="password", key="rg_pass")
                    if st.form_submit_button("Create Account", use_container_width=True):
                        r = api_post(
                            "/auth/register",
                            {"full_name": full_name, "email": email_r, "password": pass_r},
                            use_auth=False,
                        )
                        if r and r.status_code == 201:
                            st.success("✅ Account created! Please login.")
                        elif r:
                            st.error(r.json().get("detail", "Registration failed"))
            return False


def require_auth():
    """Call at top of each page. Stops rendering if not logged in."""
    logged_in = sidebar_auth()
    if not logged_in:
        st.info("👈 Please login or register using the sidebar.")
        st.stop()
