import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

# Utility functions
def calculate_marks(completion, total=5):
    return round((completion / 100) * total, 2)

def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Task Completion Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    for i, row in df.iterrows():
        line = f"{row['Task']} - Status: {row['Status']}, Marks: {row['Marks']}"
        pdf.multi_cell(0, 10, line)
    pdf.output("/tmp/report.pdf")
    return open("/tmp/report.pdf", "rb").read()

# Sidebar: Login role
st.sidebar.header("🔐 Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Reporting Officer", "Client"])

# Branding and title
st.image("https://companieslogo.com/img/orig/GMDCLTD.NS-26174231.png?t=1720244492", width=100)
st.title("📊 Task Completion Tracker")
st.markdown("A powerful tool to track, evaluate, and approve task progress.")

# Employee role
if role == "Employee":
    st.header("🧑‍💼 Submit Your Tasks")
    if not st.session_state["submitted"]:
        with st.expander("➕ Add Task"):
            task_name = st.text_input("Task Name")
            task_desc = st.text_area("Task Description")
            if st.button("Add Task") and task_name:
                if len(st.session_state["tasks"]) < 6:
                    st.session_state["tasks"].append({
                        "Task": task_name,
                        "Description": task_desc,
                        "User Completion": 0,
                        "Officer Completion": 0,
                        "Client Feedback": "",
                        "Status": "Draft",
                        "Marks": 0
                    })
                    st.success(f"✅ Task '{task_name}' added.")
                    st.rerun()
                else:
                    st.warning("⚠️ Max 6 tasks allowed.")

    for i, task in enumerate(st.session_state["tasks"]):
        if task["Status"] == "Draft":
            st.subheader(task["Task"])
            st.caption(task["Description"])
            st.session_state[f"user_completion_{i}"] = st.slider(
                "Your Completion (%)", 0, 100, task["User Completion"], 5, key=f"user_slider_{i}"
            )

    if not st.session_state["submitted"] and st.button("✅ Submit All Tasks"):
        for i, task in enumerate(st.session_state["tasks"]):
            if task["Status"] == "Draft":
                task["User Completion"] = st.session_state[f"user_completion_{i}"]
                task["Status"] = "Submitted"
        st.session_state["submitted"] = True
        st.success("🎉 Submitted! You can’t edit now.")

    # Show status summary
    st.markdown("### 📋 Task Status")
    df = pd.DataFrame(st.session_state["tasks"])
    st.dataframe(df[["Task", "Status", "Marks"]])

# Reporting Officer role
elif role == "Reporting Officer":
    st.header("🕵️ Review Submitted Tasks")
    pending_tasks = [t for t in st.session_state["tasks"] if t["Status"] == "Submitted"]
    if not pending_tasks:
        st.info("✅ All submitted tasks reviewed.")
    else:
        for i, task in enumerate(st.session_state["tasks"]):
            if task["Status"] == "Submitted":
                st.subheader(f"📌 {task['Task']}")
                st.caption(task["Description"])
                officer_completion = st.slider(
                    "Adjust Completion (%)", 0, 100,
                    task["User Completion"], 5, key=f"officer_slider_{i}"
                )
                marks = calculate_marks(officer_completion)
                task["Officer Completion"] = officer_completion
                task["Marks"] = marks
                task["Status"] = "Reviewed"
                st.success(f"Marks: {marks} / 5")

    if st.button("✔️ Finalize All Reviews"):
        st.success("✅ Review finalized!")

# Client role
elif role == "Client":
    st.header("🧑‍💼 Client Review & Approval")
    for i, task in enumerate(st.session_state["tasks"]):
        if task["Status"] == "Reviewed":
            st.subheader(f"{task['Task']} ({task['Marks']}/5)")
            st.caption(task["Description"])
            feedback = st.text_area("Your Feedback", key=f"feedback_{i}")
            status = st.selectbox("Approval", ["Pending", "Approved", "Rejected"], key=f"client_status_{i}")
            if st.button(f"💾 Save Feedback for {task['Task']}", key=f"save_btn_{i}"):
                task["Client Feedback"] = feedback
                task["Status"] = status
                st.success("✅ Feedback saved!")

# Dashboard View
st.markdown("---")
st.header("📊 Dashboard")

if st.session_state["tasks"]:
    df = pd.DataFrame(st.session_state["tasks"])
    status_filter = st.selectbox("📌 Filter by Status", ["All"] + list(df["Status"].unique()))
    if status_filter != "All":
        df = df[df["Status"] == status_filter]
    st.dataframe(df[["Task", "Status", "User Completion", "Officer Completion", "Marks", "Client Feedback"]])
else:
    st.info("No tasks found yet.")

# Export Section
st.sidebar.header("📥 Export Report")
if st.session_state["tasks"]:
    df = pd.DataFrame(st.session_state["tasks"])
    total = sum(t["Marks"] for t in st.session_state["tasks"])
    df.loc[len(df.index)] = ["Total", "", "", "", "", "", total]

    csv = df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button("📂 Download CSV", data=csv, file_name="task_report.csv", mime="text/csv")

    pdf = generate_pdf(df)
    st.sidebar.download_button("📄 Download PDF", data=pdf, file_name="task_report.pdf", mime="application/pdf")
