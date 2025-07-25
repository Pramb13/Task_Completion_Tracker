import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config("Task Completion Tracker", layout="wide")

# --- Dummy Credentials ---
users = {
    "employee1": {"password": "emp123", "role": "Employee"},
    "officer1": {"password": "off123", "role": "Officer"},
}

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- Login ---
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")

# --- Employee View ---
def employee_view():
    st.title(f"👷 Employee Dashboard - {st.session_state.username}")

    with st.form("add_task_form"):
        task_name = st.text_input("Task Name")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Submit Task")

        if submitted and task_name:
            st.session_state.tasks.append({
                "Employee": st.session_state.username,
                "Task Name": task_name,
                "Description": description,
                "Status": "Draft",
                "Marks": 0,
                "Reviewed": False,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("✅ Task submitted!")

    st.markdown("---")
    st.subheader("📋 Your Tasks")

    for i, task in enumerate(st.session_state.tasks):
        if task["Employee"] == st.session_state.username:
            st.markdown(f"**Task {i+1}: {task['Task Name']}**")
            task["Status"] = st.selectbox(
                f"Status for Task {i+1}", 
                ["Draft", "Submitted", "Completed"], 
                index=["Draft", "Submitted", "Completed"].index(task["Status"]),
                key=f"status_{i}"
            )
            task["Marks"] = st.slider(
                f"Marks (out of 10) for Task {i+1}", 
                0, 10, int(task.get("Marks", 0)), 
                key=f"marks_slider_{i}"
            )

# --- Officer View ---
def officer_view():
    st.title(f"🧑‍💼 Reporting Officer Dashboard - {st.session_state.username}")

    st.subheader("📌 Tasks Pending Review")

    reviewed_count = 0
    for i, task in enumerate(st.session_state.tasks):
        if task["Status"] == "Completed" and not task["Reviewed"]:
            st.markdown(f"**From: {task['Employee']} | Task: {task['Task Name']}**")
            st.markdown(f"> {task['Description']}")
            st.markdown(f"Marks Given: {task['Marks']}")
            if st.button(f"Mark Reviewed - Task {i+1}"):
                st.session_state.tasks[i]["Reviewed"] = True
                st.success("✅ Task marked as reviewed")
                reviewed_count += 1

    if reviewed_count == 0:
        st.info("No pending tasks to review.")

    st.markdown("---")
    st.subheader("📤 Export All Tasks")
    if st.button("Download CSV"):
        df = pd.DataFrame(st.session_state.tasks)
        df.to_csv("tasks.csv", index=False)
        st.download_button("📄 Click to Download", data=df.to_csv(index=False), file_name="tasks.csv", mime="text/csv")

# --- Main ---
if not st.session_state.logged_in:
    login()
else:
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.experimental_rerun()

    if st.session_state.role == "Employee":
        employee_view()
    elif st.session_state.role == "Officer":
        officer_view()
