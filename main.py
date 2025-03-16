import streamlit as st
import pandas as pd

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False  # Track if submission is done

# Function to calculate marks
def calculate_marks(completion_percentage, total_marks=5):
    return round(total_marks * (completion_percentage / 100), 2)

# User authentication
st.sidebar.header("🔑 Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Reporting Officer"])

# App title with logo
st.image("https://companieslogo.com/img/orig/GMDCLTD.NS-26174231.png?t=1720244492", width=100)  # Company logo
st.title("📊 Task Completion Tracker")
st.markdown("### A streamlined way to track and evaluate task progress.")

# Employee Section
if role == "Employee":
    st.header("📝 Add or Update Your Tasks")

    if not st.session_state["submitted"]:  # Allow adding tasks only if not submitted
        new_task_name = st.text_input("Enter a new task name:")
        if st.button("➕ Add Task") and new_task_name:
            if len(st.session_state["tasks"]) < 6:  # Max 6 tasks allowed
                st.session_state["tasks"].append({"Task": new_task_name, "User Completion": 0, "Officer Completion": 0, "Marks": 0})
                st.success(f"Task '{new_task_name}' added successfully!")
                st.rerun()

    # Update completion percentages
    if st.session_state["tasks"]:
        for task in st.session_state["tasks"]:
            task["User Completion"] = st.slider(f'📌 {task["Task"]} Completion', 0, 100, task["User Completion"], 5)

        if not st.session_state["submitted"]:  # Only allow submission once
            if st.button("✅ Submit Completion"):
                st.session_state["submitted"] = True
                st.success("✅ Task completion submitted successfully! You can no longer edit tasks.")

# Reporting Officer Section
elif role == "Reporting Officer":
    st.header("📋 Review & Adjust Task Completion")
    total_marks_obtained = 0

    if st.session_state["tasks"]:
        for task in st.session_state["tasks"]:
            st.write(f"📌 **{task['Task']}**: {task['User Completion']}% completed by employee")
            task["Officer Completion"] = st.slider(f"Adjust completion for {task['Task']}", 0, 100, task["User Completion"], 5)
            task["Marks"] = calculate_marks(task["Officer Completion"])
            total_marks_obtained += task["Marks"]
            st.progress(task["Officer Completion"] / 100)
            st.write(f"🔹 Marks: **{task['Marks']} out of 5**")

        st.subheader(f"🏆 Total Marks Obtained: **{total_marks_obtained} out of 30**")

        if st.button("✔️ Finalize Review"):
            st.success("✅ Reporting Officer's review has been saved!")

# Export Report Section
st.sidebar.header("📥 Export Report")

if st.session_state["tasks"]:
    df = pd.DataFrame(st.session_state["tasks"])
    
    # Calculate total marks
    total_marks = sum(task["Marks"] for task in st.session_state["tasks"])
    df.loc[len(df.index)] = ["Total", "", "", total_marks]  # Add total row

    # CSV Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button("📂 Download CSV", data=csv, file_name="task_report.csv", mime="text/csv")
