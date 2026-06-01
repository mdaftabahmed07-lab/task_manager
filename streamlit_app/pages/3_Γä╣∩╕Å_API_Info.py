"""
ℹ️ API Info — endpoint reference + live tester
"""

import streamlit as st
from api_client import inject_css, page_header, require_auth, get_base_url, api_get

st.set_page_config(page_title="API Info", page_icon="ℹ️", layout="wide")
inject_css()
require_auth()
page_header("ℹ️ API Reference")

# ── Token viewer ───────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("👤 Current User")
    st.json(st.session_state.get("user") or {})

with col_b:
    st.subheader("🔑 JWT Token")
    token = st.session_state.get("token") or ""
    st.code(f"Bearer {token[:50]}..." if token else "—", language="text")
    st.caption("Use this in the Authorization header for all /tasks requests.")

st.divider()

# ── Endpoint table ─────────────────────────────────────────────────────────
st.subheader("📡 Endpoints")

base = get_base_url()
endpoints = [
    ("POST",   "/auth/register",  "Register a new user",                   False, "#16a34a"),
    ("POST",   "/auth/login",     "Login — receive JWT token",              False, "#16a34a"),
    ("POST",   "/tasks",          "Create a task",                          True,  "#16a34a"),
    ("GET",    "/tasks",          "List tasks (filter, search, paginate)",  True,  "#0284c7"),
    ("GET",    "/tasks/{id}",     "Get a single task by ID",                True,  "#0284c7"),
    ("PUT",    "/tasks/{id}",     "Update a task (partial update OK)",      True,  "#d97706"),
    ("DELETE", "/tasks/{id}",     "Delete a task permanently",              True,  "#dc2626"),
]

for method, path, desc, auth, color in endpoints:
    lock = "🔒" if auth else "🔓"
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:1rem;padding:.6rem 1rem;
                        background:white;border-radius:8px;margin-bottom:.4rem;
                        box-shadow:0 1px 4px rgba(0,0,0,0.07)">
                <span style="background:{color};color:white;border-radius:4px;
                             padding:2px 10px;font-family:monospace;font-weight:700;
                             font-size:.78rem;min-width:60px;text-align:center">{method}</span>
                <code style="color:#334155;font-size:.88rem">{base}{path}</code>
                <span style="color:#64748b;font-size:.82rem;margin-left:auto">{lock} {desc}</span>
            </div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    f"📚 [Open Swagger UI →]({base}/docs)  ·  [Open ReDoc →]({base}/redoc)",
    unsafe_allow_html=False,
)

st.divider()

# ── Live tester ────────────────────────────────────────────────────────────
st.subheader("🔬 Live Tester — GET /tasks/{id}")
task_id = st.number_input("Task ID", min_value=1, step=1, value=1)
if st.button("Fetch Task"):
    r = api_get(f"/tasks/{task_id}")
    if r and r.status_code == 200:
        st.json(r.json())
    elif r:
        st.error(r.json().get("detail", "Task not found"))

st.divider()

# ── Enum reference ─────────────────────────────────────────────────────────
st.subheader("📖 Enum Values")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Priority**")
    st.markdown("- `low`\n- `medium`\n- `high`")
with c2:
    st.markdown("**Status**")
    st.markdown("- `todo`\n- `in_progress`\n- `done`")
