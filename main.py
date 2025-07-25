import streamlit as st
import pandas as pd

st.set_page_config(page_title="Task Completion Tracker", layout="wide")

# Initialize session state for tasks and user roles
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

# Normalize all tasks to prevent KeyError (even for old ones)
for task in st.session_state["tasks"]:
    task.setdefault("Task", "")
    task.setdefault("Description", "")
    task.setdefault("User Completion", 0)
    task.setdefault("Officer Completion", 0)
    task.setdefault("Client Feedback", "")
    task.setdefault("Status", "Draft")
    task.setdefault("Marks", 0)

# Sidebar for role selection
role = st.sidebar.radio("Select Your Role", ["Employee", "Reporting Officer", "Client", "Dashboard"])

# ------------------------ Employee View ------------------------
if role == "Employee":
    st.header("👨‍💼 Employee Task Submission")

    with st.form("employee_form"):
        task_name = st.text_input("Task Name")
        task_desc = st.text_area("Task Description")
        submitted = st.form_submit_button("Add Task")
        if submitted:
            st.session_state["tasks"].append({
                "Task": task_name,
                "Description": task_desc,
                "User Completion": 0,
                "Officer Completion": 0,
                "Client Feedback": "",
                "Status": "Draft",
                "Marks": 0
            })
            st.success("Task added successfully!")

    st.subheader("📋 Your Draft Tasks")

    for i, task in enumerate(st.session_state["tasks"]):
        if task.get("Status", "Draft") == "Draft":
            st.markdown(f"**Task {i+1}:** {task['Task']}")
            st.write(task["Description"])
            completion = st.slider("Completion %", 0, 100, task["User Completion"], key=f"user_slider_{i}")
            st.session_state["tasks"][i]["User Completion"] = completion
            if st.button("Submit Task", key=f"submit_task_{i}"):
                st.session_state["tasks"][i]["Status"] = "Submitted"
                st.success(f"Task {i+1} submitted.")

# ------------------------ Reporting Officer View ------------------------
elif role == "Reporting Officer":
    st.header("🧑‍💻 Review Submitted Tasks")

    for i, task in enumerate(st.session_state["tasks"]):
        if task.get("Status", "Draft") != "Draft" and task.get("Status") != "Reviewed":
            st.markdown(f"**Task {i+1}:** {task['Task']}")
            st.write(task["Description"])
            st.write(f"Employee Completion: {task['User Completion']}%")
            review = st.slider("Review Completion %", 0, 100, task["Officer Completion"], key=f"officer_slider_{i}")
            marks = st.slider("Marks (out of 10)", 0, 10, task["Marks"], key=f"marks_slider_{i}")
            st.session_state["tasks"][i]["Officer Completion"] = review
            st.session_state["tasks"][i]["Marks"] = marks
            if st.button("Mark as Reviewed", key=f"review_task_{i}"):
                st.session_state["tasks"][i]["Status"] = "Reviewed"
                st.success(f"Task {i+1} marked as reviewed.")

# ------------------------ Client View ------------------------
elif role == "Client":
    st.header("🧑‍⚖️ Client Task Review")

    for i, task in enumerate(st.session_state["tasks"]):
        if task.get("Status") == "Reviewed":
            st.markdown(f"**Task {i+1}:** {task['Task']}")
            st.write(task["Description"])
            st.write(f"Employee Completion: {task['User Completion']}%")
            st.write(f"Officer Review: {task['Officer Completion']}%")
            st.write(f"Marks Awarded: {task['Marks']} / 10")
            feedback = st.text_area("Client Feedback", task["Client Feedback"], key=f"client_feedback_{i}")
            st.session_state["tasks"][i]["Client Feedback"] = feedback
            if st.button("Finalize Task", key=f"finalize_task_{i}"):
                st.session_state["tasks"][i]["Status"] = "Completed"
                st.success(f"Task {i+1} marked as Completed.")

# ------------------------ Dashboard ------------------------
elif role == "Dashboard":
    st.header("📊 Task Dashboard")

    df = pd.DataFrame(st.session_state["tasks"])

    if df.empty:
        st.warning("No tasks added yet.")
    else:
        st.dataframe(df)

        # Count stats
        pending_after_review = df[df["Status"] == "Reviewed"]
        completed = df[df["Status"] == "Completed"]
        draft = df[df["Status"] == "Draft"]
        submitted = df[df["Status"] == "Submitted"]

        st.subheader("🔎 Status Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📝 Draft", len(draft))
        col2.metric("📤 Submitted", len(submitted))
        col3.metric("🕵️ Reviewed", len(pending_after_review))
        col4.metric("✅ Completed", len(completed))

        # Downloadable CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Task Report as CSV",
            data=csv,
            file_name='task_report.csv',
            mime='text/csv',
        )
