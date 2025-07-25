import streamlit as st
import json
import os
import pandas as pd

# Load users from user.json
@st.cache_data
def load_users():
    with open("user.json") as f:
        return json.load(f)

# Initialize task storage in session state
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""

users = load_users()

def login():
    st.title("🔐 Task Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        for user in users:
            if user["username"] == username and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.experimental_rerun()
        st.error("❌ Invalid credentials")

def employee_dashboard():
    st.title("👷 Employee Dashboard")
    task_name = st.text_input("Task Name")
    description = st.text_area("Task Description")
    if st.button("Add Task"):
        task = {
            "Task": task_name,
            "Description": description,
            "Status": "Draft",
            "Marks": None,
            "Client_Review": ""
        }
        st.session_state.tasks.append(task)
        st.success("✅ Task added!")

    for i, task in enumerate(st.session_state.tasks):
        st.markdown(f"### Task {i+1}: {task['Task']}")
        st.write(f"**Description:** {task['Description']}")
        st.write(f"**Status:** {task['Status']}")
        if task["Status"] == "Draft":
            if st.button("Submit Task", key=f"submit_{i}"):
                task["Status"] = "Submitted"
                st.success("✅ Task submitted!")


def officer_dashboard():
    st.title("🧑‍💼 Reporting Officer Dashboard")

    for i, task in enumerate(st.session_state.tasks):
        if task["Status"] == "Submitted":
            st.markdown(f"### Task {i+1}: {task['Task']}")
            st.write(f"**Description:** {task['Description']}")
            marks = st.slider("Marks (out of 10)", 0, 10, task["Marks"] or 0, key=f"marks_slider_{i}")
            if st.button("Review & Approve", key=f"review_{i}"):
                task["Marks"] = marks
                task["Status"] = "Reviewed"
                st.success("✅ Task reviewed and approved!")


def client_dashboard():
    st.title("📋 Client Task Review")
    tasks = st.session_state.tasks

    for i, task in enumerate(tasks):
        if task["Status"] in ["Submitted", "Reviewed"]:
            st.markdown(f"### Task {i+1}: {task['Task']}")
            st.write(f"**Description:** {task['Description']}")
            st.write(f"**Status:** {task['Status']}")
            st.write(f"**Marks:** {task['Marks'] if task['Marks'] is not None else 'Not Scored'}")
            st.write(f"**Previous Client Review:** {task.get('Client_Review', 'No review')}")
            review = st.text_area("Add your review", value=task.get("Client_Review", ""), key=f"review_{i}")
            if st.button("Submit Review", key=f"submit_review_{i}"):
                task["Client_Review"] = review
                st.success("✅ Review submitted!")


def logout():
    if st.sidebar.button("🔓 Logout"):
        for k in ["logged_in", "username", "role"]:
            st.session_state[k] = False if k == "logged_in" else ""
        st.experimental_rerun()

if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("Navigation")
    st.sidebar.write(f"👤 Logged in as: `{st.session_state.username}` ({st.session_state.role})")
    logout()

    if st.session_state.role == "employee":
        employee_dashboard()
    elif st.session_state.role == "officer":
        officer_dashboard()
    elif st.session_state.role == "client":
        client_dashboard()
    else:
        st.error("❌ Unknown role.")
