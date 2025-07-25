import streamlit as st
import pandas as pd

# ---------- USER DATABASE ----------
users = {
    "employee": {"password": "emp123", "role": "Employee"},
    "officer": {"password": "off123", "role": "Officer"}
}

# ---------- SESSION SETUP ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.tasks = []  # List of task dicts

# ---------- LOGIN FUNCTION ----------
def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid credentials")

# ---------- LOGOUT FUNCTION ----------
def logout():
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.tasks = []

# ---------- EMPLOYEE DASHBOARD ----------
def employee_view():
    st.header("📝 Employee Dashboard")
    
    with st.form("add_task_form"):
        task_name = st.text_input("Task Name")
        description = st.text_area("Description")
        submit = st.form_submit_button("Add Task")
        if submit and task_name:
            st.session_state.tasks.append({
                "Task": task_name,
                "Description": description,
                "Status": "Draft",
                "Marks": 0
            })
            st.success("Task added as Draft.")

    # View & Submit Tasks
    for i, task in enumerate(st.session_state.tasks):
        if task["Status"] == "Draft":
            st.markdown(f"**📝 Task {i+1}:** {task['Task']}")
            new_name = st.text_input("Edit Task Name", task["Task"], key=f"name_{i}")
            new_desc = st.text_area("Edit Description", task["Description"], key=f"desc_{i}")
            if st.button("Submit Task", key=f"submit_{i}"):
                st.session_state.tasks[i]["Task"] = new_name
                st.session_state.tasks[i]["Description"] = new_desc
                st.session_state.tasks[i]["Status"] = "Submitted"
                st.success("✅ Task submitted for review.")

    st.subheader("📤 Submitted Tasks")
    submitted_tasks = [t for t in st.session_state.tasks if t["Status"] == "Submitted"]
    st.table(pd.DataFrame(submitted_tasks))

# ---------- OFFICER DASHBOARD ----------
def officer_view():
    st.header("📋 Officer Dashboard")
    
    pending_tasks = [t for t in st.session_state.tasks if t["Status"] == "Submitted"]
    completed_tasks = [t for t in st.session_state.tasks if t["Status"] == "Reviewed"]

    st.subheader("🕒 Tasks Pending Review")
    if not pending_tasks:
        st.info("No tasks pending review.")
    for i, task in enumerate(pending_tasks):
        st.markdown(f"**📝 Task {i+1}: {task['Task']}**")
        st.write(task["Description"])
        marks = st.slider("Marks (out of 10)", 0, 10, 0, key=f"marks_slider_{i}")
        if st.button("Mark as Reviewed", key=f"review_{i}"):
            index = st.session_state.tasks.index(task)
            st.session_state.tasks[index]["Marks"] = marks
            st.session_state.tasks[index]["Status"] = "Reviewed"
            st.success("✅ Task marked as reviewed.")

    st.subheader("✅ Reviewed Tasks")
    if completed_tasks:
        st.table(pd.DataFrame(completed_tasks))
    else:
        st.info("No reviewed tasks yet.")

# ---------- MAIN ----------
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("👋 Welcome")
    st.sidebar.write(f"Logged in as: `{st.session_state.username}` ({st.session_state.role})")
    logout()

    if st.session_state.role == "Employee":
        employee_view()
    elif st.session_state.role == "Officer":
        officer_view()
