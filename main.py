import streamlit as st
import json
import os
from datetime import datetime

# Load user data from users.json
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return []

# Load task database
def load_tasks():
    if os.path.exists("task_database.json"):
        with open("task_database.json", "r") as f:
            return json.load(f)
    return []

# Save task database
def save_tasks(tasks):
    with open("task_database.json", "w") as f:
        json.dump(tasks, f, indent=4)

# Authenticate user
def authenticate(username, password, role):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password and user["role"] == role:
            return True
    return False

# Employee Task Submission
def employee_view(username):
    st.header("🧑‍💼 Employee - Submit Task")
    tasks = load_tasks()

    task_name = st.text_input("Task Title")
    description = st.text_area("Task Description")

    if st.button("Submit Task"):
        task = {
            "task_name": task_name,
            "description": description,
            "submitted_by": username,
            "status": "Submitted",
            "completion": 0,
            "review": "",
            "client_review": "",
            "timestamp": str(datetime.now())
        }
        tasks.append(task)
        save_tasks(tasks)
        st.success("✅ Task submitted successfully!")

    st.subheader("Your Task Status")
    for task in tasks:
        if task["submitted_by"] == username:
            icon = "✅" if task["status"] == "Completed" else "⏳"
            st.write(f"- {task['task_name']} ({task['status']}) {icon}")

# RO Task Review
def ro_view():
    st.header("🧑‍💼 Reporting Officer - Review Tasks")
    tasks = load_tasks()
    updated = False

    for idx, task in enumerate(tasks):
        if task["status"] == "Submitted":
            with st.expander(f"📌 {task['task_name']} by {task['submitted_by']}"):
                st.write(task["description"])
                completion = st.slider("Completion %", 0, 100, task["completion"], key=f"slider_{idx}")
                review = st.text_area("Review Comments", task["review"], key=f"review_{idx}")
                if st.button(f"Submit Review {idx}"):
                    tasks[idx]["completion"] = completion
                    tasks[idx]["review"] = review
                    tasks[idx]["status"] = "Reviewed"
                    updated = True
                    st.success("✅ Review submitted.")

    if updated:
        save_tasks(tasks)

# Client Final Review
def client_view():
    st.header("👤 Client - Final Review")
    tasks = load_tasks()
    updated = False

    for idx, task in enumerate(tasks):
        if task["status"] == "Reviewed":
            with st.expander(f"✅ {task['task_name']} by {task['submitted_by']}"):
                st.write(f"📄 Description: {task['description']}")
                st.write(f"📊 Completion: {task['completion']}%")
                st.write(f"📝 RO Review: {task['review']}")
                client_feedback = st.text_area("Client Feedback", task.get("client_review", ""), key=f"client_{idx}")
                if st.button(f"Finalize Review {idx}"):
                    tasks[idx]["client_review"] = client_feedback
                    tasks[idx]["status"] = "Completed"
                    updated = True
                    st.success("✅ Client review submitted.")

    if updated:
        save_tasks(tasks)

    st.subheader("📊 Tasks Pending Client Review")
    for task in tasks:
        if task["status"] == "Reviewed":
            st.warning(f"- {task['task_name']} by {task['submitted_by']}")

# Sidebar Login + Role
def login_sidebar():
    st.sidebar.title("🔐 Login")
    role = st.sidebar.selectbox("Select Role", ["Employee", "Reporting Officer", "Client"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")
    return role, username, password, login_btn

# ---------------------- APP --------------------------
st.set_page_config(page_title="Task Tracker", layout="centered")
st.title("📋 Task Completion Tracker")

role, username, password, login_btn = login_sidebar()

if login_btn:
    if authenticate(username, password, role):
        st.sidebar.success(f"✅ Logged in as {username} ({role})")
        if role == "Employee":
            employee_view(username)
        elif role == "Reporting Officer":
            ro_view()
        elif role == "Client":
            client_view()
    else:
        st.sidebar.error("❌ Invalid username, password or role.")
