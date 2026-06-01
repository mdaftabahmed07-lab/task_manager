"""
📋 My Tasks — list, filter, search, edit, delete
"""

import streamlit as st
from api_client import (
    inject_css, page_header, require_auth,
    load_tasks, status_badge, priority_badge, fmt_date,
    api_put, api_delete,
)

st.set_page_config(page_title="My Tasks", page_icon="📋", layout="wide")
inject_css()
require_auth()
page_header("📋 My Tasks")

# ── Filter bar ─────────────────────────────────────────────────────────────
fc1, fc2, fc3 = st.columns([3, 1, 1])
with fc1:
    search_q = st.text_input("🔍 Search", placeholder="Search title or description...")
with fc2:
    filter_status = st.selectbox("Status", ["All", "todo", "in_progress", "done"])
with fc3:
    filter_priority = st.selectbox("Priority", ["All", "high", "medium", "low"])

data  = load_tasks(
    status   = None if filter_status   == "All" else filter_status,
    priority = None if filter_priority == "All" else filter_priority,
    search   = search_q or None,
)
tasks = data.get("results", [])
st.caption(f"Showing **{len(tasks)}** of **{data.get('total', 0)}** tasks")

if not tasks:
    st.info("No tasks match your filters.")
    st.stop()

# ── Task list ──────────────────────────────────────────────────────────────
for t in tasks:
    st.markdown(
        f"""<div class="task-card {t['priority']}">
                <div class="task-title">#{t['id']} — {t['title']}</div>
                <div class="task-desc">{t.get('description') or '<em>No description</em>'}</div>
                <div class="task-meta">
                    {status_badge(t['status'])}
                    {priority_badge(t['priority'])}
                    <span style="color:#999;font-size:.78rem">{fmt_date(t['created_at'])}</span>
                </div>
            </div>""",
        unsafe_allow_html=True,
    )

    col_edit, col_del = st.columns([4, 1])

    with col_edit:
        with st.expander(f"✏️ Edit Task #{t['id']}"):
            with st.form(f"edit_{t['id']}"):
                new_title = st.text_input("Title", value=t["title"])
                new_desc  = st.text_area("Description", value=t.get("description") or "")
                c1, c2 = st.columns(2)
                with c1:
                    new_status = st.selectbox(
                        "Status", ["todo", "in_progress", "done"],
                        index=["todo", "in_progress", "done"].index(t["status"]),
                    )
                with c2:
                    new_priority = st.selectbox(
                        "Priority", ["low", "medium", "high"],
                        index=["low", "medium", "high"].index(t["priority"]),
                    )
                if st.form_submit_button("💾 Save Changes"):
                    payload = {
                        "title": new_title,
                        "description": new_desc or None,
                        "status": new_status,
                        "priority": new_priority,
                    }
                    r = api_put(f"/tasks/{t['id']}", json=payload)
                    if r and r.status_code == 200:
                        st.success("✅ Task updated!")
                        st.rerun()
                    elif r:
                        st.error(r.json().get("detail", "Update failed"))

    with col_del:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Delete", key=f"del_{t['id']}"):
            r = api_delete(f"/tasks/{t['id']}")
            if r and r.status_code == 200:
                st.success(f"Task #{t['id']} deleted.")
                st.rerun()
            elif r:
                st.error(r.json().get("detail", "Delete failed"))
