import streamlit as st
import pandas as pd
import json

# Load users from JSON
@st.cache_data
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

users = load_users()

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.username = ""
    st.session_state.tasks = []

# Login section
def login():
    st.title("🔐 Login to Task Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.role = users[username]["role"]
            st.session_state.username = username
            st.success(f"Welcome, {username}! Role: {st.session_state.role}")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

# Logout
def logout():
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.username = ""
    st.experimental_rerun()

# Task structure normalization
for task in st.session_state.tasks:
    task.setdefault("User Completion", 0)
    task.setdefault("Officer Completion", 0)
    task.setdefault("Client Feedback", "")
    task.setdefault("Status", "Draft")
    task.setdefault("Marks", 0)

# Main app logic
def main_app():
    role = st.session_state.role
    st.sidebar.title(f"👤 Logged in as: {st.session_state.username}")
    st.sidebar.button("Logout", on_click=logout)

    # Employee Section
    if role == "Employee":
        st.title("📝 Submit Your Tasks")
        with st.form("task_form"):
            task_name = st.text_input("Task Name")
            user_completion = st.slider("Your Completion (%)", 0, 100, 0)
            submitted = st.form_submit_button("Add Task")
            if submitted and task_name:
                st.session_state["tasks"].append({
                    "Task": task_name,
                    "User Completion": user_completion,
                    "Officer Completion": 0,
                    "Client Feedback": "",
                    "Status": "Draft",
                    "Marks": 0
                })
                st.success("✅ Task added successfully!")

        st.subheader("🕒 Your Draft Tasks")
        for i, task in enumerate(st.session_state["tasks"]):
            if task.get("Status") == "Draft":
                st.markdown(f"**{task['Task']}**")
                st.progress(task["User Completion"])
                if st.button("Submit for Review", key=f"submit_{i}"):
                    task["Status"] = "Submitted"
                    st.success(f"✅ '{task['Task']}' submitted for officer review.")

    # Officer Section
    elif role == "Reporting Officer":
        st.title("🔍 Review Submitted Tasks")
        submitted_tasks = [t for t in st.session_state["tasks"] if t["Status"] == "Submitted"]
        if not submitted_tasks:
            st.info("No submitted tasks yet.")
        for i, task in enumerate(submitted_tasks):
            st.markdown(f"### {task['Task']}")
            st.write(f"Employee Completion: {task['User Completion']}%")
            officer_completion = st.slider("Officer Completion", 0, 100, task["Officer Completion"], key=f"officer_slider_{i}")
            marks = st.slider("Marks (0-10)", 0, 10, int(task["Marks"]), key=f"marks_{i}")
            if st.button("Review Task", key=f"review_{i}"):
                task["Officer Completion"] = officer_completion
                task["Marks"] = marks
                task["Status"] = "Reviewed"
                st.success(f"🟢 Task '{task['Task']}' reviewed.")

    # Client Section
    elif role == "Client":
        st.title("💬 Client Feedback")
        reviewed_tasks = [t for t in st.session_state["tasks"] if t["Status"] == "Reviewed"]
        if not reviewed_tasks:
            st.info("No tasks available for feedback.")
        for i, task in enumerate(reviewed_tasks):
            st.markdown(f"### {task['Task']}")
            st.write(f"Completion by Officer: {task['Officer Completion']}%")
            st.write(f"Marks: {task['Marks']}/10")
            feedback = st.text_input("Feedback", key=f"feedback_{i}", value=task.get("Client Feedback", ""))
            if st.button("Submit Feedback", key=f"submit_feedback_{i}"):
                task["Client Feedback"] = feedback
                task["Status"] = "Completed"
                st.success(f"✅ Feedback submitted for '{task['Task']}'.")

    # Admin Dashboard
    elif role == "Dashboard":
        st.title("📊 Admin Task Dashboard")
        pending_tasks = [t for t in st.session_state["tasks"] if t["Status"] != "Completed"]
        if not pending_tasks:
            st.success("✅ All tasks completed.")
        else:
            st.warning(f"⚠️ {len(pending_tasks)} task(s) pending.")
            df = pd.DataFrame(pending_tasks)
            st.dataframe(df)
            st.download_button("📥 Download Pending Tasks", df.to_csv(index=False), file_name="pending_tasks.csv")

# App routing
if not st.session_state.authenticated:
    login()
else:
    main_app()

st.markdown("---")
st.caption("🔒 Task Completion Tracker with Login | © 2025")
