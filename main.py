import streamlit as st
import json
import os
from datetime import datetime

# Load user data
@st.cache_data
def load_users():
    with open("user.json") as f:
        return json.load(f)

# Load task database
def load_tasks():
    if os.path.exists("task_database.json"):
        with open("task_database.json", "r") as f:
            return json.load(f)
    else:
        return []

# Save task database
def save_tasks(tasks):
    with open("task_database.json", "w") as f:
        json.dump(tasks, f, indent=4)

# Login function
def login():
    st.title("🔐 Task Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        for user in users:
            if user.get("username") == username and user.get("password") == password:
                st.session_state["logged_in"] = True
                st.session_state["role"] = user["role"]
                st.session_state["username"] = username
                st.rerun()
        st.error("❌ Invalid credentials")

# Employee Task Submission
def employee_view():
    st.title("🧑‍💼 Employee - Submit Task")
    tasks = load_tasks()

    task_name = st.text_input("Task Title")
    description = st.text_area("Task Description")
    if st.button("Submit Task"):
        task = {
            "task_name": task_name,
            "description": description,
            "submitted_by": st.session_state["username"],
            "status": "Submitted",
            "completion": 0,
            "review": "",
            "client_review": "",
            "timestamp": str(datetime.now())
        }
        tasks.append(task)
        save_tasks(tasks)
        st.success("✅ Task submitted successfully!")

    # View pending review tasks
    st.subheader("Tasks pending review")
    for task in tasks:
        if task["submitted_by"] == st.session_state["username"] and task["status"] == "Reviewed":
            st.write(f"- {task['task_name']} ✅ Reviewed by RO")
        elif task["submitted_by"] == st.session_state["username"] and task["status"] == "Submitted":
            st.write(f"- {task['task_name']} ⏳ Waiting for review")

# Reporting Officer View
def ro_view():
    st.title("🧑‍💼 Reporting Officer - Review Tasks")
    tasks = load_tasks()
    updated = False

    for idx, task in enumerate(tasks):
        if task["status"] == "Submitted":
            with st.expander(f"📌 {task['task_name']} by {task['submitted_by']}"):
                st.write(task["description"])
                completion = st.slider("Completion %", 0, 100, task["completion"])
                review = st.text_area("Review Comments", task["review"])
                if st.button(f"Submit Review {idx}"):
                    tasks[idx]["completion"] = completion
                    tasks[idx]["review"] = review
                    tasks[idx]["status"] = "Reviewed"
                    updated = True
                    st.success("Review submitted.")

    if updated:
        save_tasks(tasks)

# Client View
def client_view():
    st.title("👤 Client - Give Final Review")
    tasks = load_tasks()
    updated = False

    for idx, task in enumerate(tasks):
        if task["status"] == "Reviewed":
            with st.expander(f"✅ {task['task_name']} by {task['submitted_by']}"):
                st.write(f"Description: {task['description']}")
                st.write(f"RO Completion: {task['completion']}%")
                st.write(f"RO Review: {task['review']}")
                client_feedback = st.text_area("Your Review", task.get("client_review", ""), key=f"client_{idx}")
                if st.button(f"Finalize Review {idx}"):
                    tasks[idx]["client_review"] = client_feedback
                    tasks[idx]["status"] = "Completed"
                    updated = True
                    st.success("Client review saved.")

    if updated:
        save_tasks(tasks)

    st.subheader("📊 Pending Reviews")
    for task in tasks:
        if task["status"] == "Reviewed":
            st.warning(f"- {task['task_name']} by {task['submitted_by']}")

# App entry
if "logged_in" not in st.session_state:
    login()
else:
    st.sidebar.title("🎯 Task Tracker")
    st.sidebar.success(f"Logged in as: {st.session_state['role'].capitalize()}")

    if st.session_state["role"] == "employee":
        employee_view()
    elif st.session_state["role"] == "ro":
        ro_view()
    elif st.session_state["role"] == "client":
        client_view()
    else:
        st.error("Unknown role!")
