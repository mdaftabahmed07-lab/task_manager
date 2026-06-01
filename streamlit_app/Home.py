"""
🏠 Home — Task Manager Dashboard
"""

import streamlit as st
from api_client import inject_css, page_header, require_auth, load_tasks, status_badge, priority_badge, fmt_date

st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
require_auth()

page_header("✅ Task Manager", "Reachware Studio — FastAPI Assessment")

# ── Stats ──────────────────────────────────────────────────────────────────
all_data = load_tasks()
tasks = all_data.get("results", [])

total       = len(tasks)
todo_n      = sum(1 for t in tasks if t["status"] == "todo")
inprog_n    = sum(1 for t in tasks if t["status"] == "in_progress")
done_n      = sum(1 for t in tasks if t["status"] == "done")
high_n      = sum(1 for t in tasks if t["priority"] == "high")

c1, c2, c3, c4, c5 = st.columns(5)
for col, num, label, color in [
    (c1, total,   "Total Tasks",   "#334155"),
    (c2, todo_n,  "To Do",         "#0284c7"),
    (c3, inprog_n,"In Progress",   "#d97706"),
    (c4, done_n,  "Done",          "#16a34a"),
    (c5, high_n,  "High Priority", "#dc2626"),
]:
    col.markdown(
        f'<div class="stat-card"><div class="stat-num" style="color:{color}">{num}</div>'
        f'<div class="stat-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ─────────────────────────────────────────────────────────────────
if tasks:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📊 Status Breakdown")
        st.bar_chart({"To Do": todo_n, "In Progress": inprog_n, "Done": done_n})

    with col_b:
        st.subheader("🎯 Priority Breakdown")
        st.bar_chart({
            "High":   high_n,
            "Medium": sum(1 for t in tasks if t["priority"] == "medium"),
            "Low":    sum(1 for t in tasks if t["priority"] == "low"),
        })

    # ── Recent tasks ────────────────────────────────────────────────────────
    st.subheader("🕐 Recent Tasks")
    recent = sorted(tasks, key=lambda t: t["created_at"], reverse=True)[:5]
    for t in recent:
        st.markdown(
            f"""<div class="task-card {t['priority']}">
                    <div class="task-title">{t['title']}</div>
                    <div class="task-desc">{t.get('description') or '<em>No description</em>'}</div>
                    <div class="task-meta">
                        {status_badge(t['status'])}
                        {priority_badge(t['priority'])}
                        <span style="color:#999;font-size:.78rem">#{t['id']} · {fmt_date(t['created_at'])}</span>
                    </div>
                </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("No tasks yet. Go to **📋 My Tasks** → Create Task to add your first one!")
