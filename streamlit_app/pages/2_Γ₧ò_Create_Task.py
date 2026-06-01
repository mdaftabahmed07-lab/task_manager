"""
➕ Create Task
"""

import streamlit as st
from api_client import inject_css, page_header, require_auth, api_post

st.set_page_config(page_title="Create Task", page_icon="➕", layout="wide")
inject_css()
require_auth()
page_header("➕ Create Task")

with st.form("create_task_form"):
    title = st.text_input("Title *", placeholder="e.g. Set up CI/CD pipeline")
    description = st.text_area("Description", placeholder="Optional details about the task...")

    c1, c2 = st.columns(2)
    with c1:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
    with c2:
        status = st.selectbox("Status", ["todo", "in_progress", "done"])

    submitted = st.form_submit_button("🚀 Create Task", use_container_width=True)

if submitted:
    if not title.strip():
        st.error("❌ Title is required.")
    else:
        payload = {
            "title": title.strip(),
            "description": description.strip() or None,
            "priority": priority,
            "status": status,
        }
        r = api_post("/tasks", json=payload)
        if r and r.status_code == 201:
            task = r.json()
            st.success(f"✅ Task **#{task['id']} — {task['title']}** created successfully!")
            st.balloons()
            st.info("Go to **📋 My Tasks** to view and manage it.")
        elif r:
            st.error(r.json().get("detail", "Task creation failed"))
