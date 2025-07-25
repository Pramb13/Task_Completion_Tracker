import streamlit as st
import pandas as pd
from fpdf import FPDF

# App title and sidebar
st.set_page_config(page_title="Task Completion Tracker", layout="wide")
st.title("📋 Task Completion Tracker")

# Sidebar Role Selection
role = st.sidebar.selectbox("Select Role", ["Employee", "Reporting Officer", "Client"])

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

# Function to generate PDF
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Task Completion Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    for i, row in df.iterrows():
        if row["Task"] == "Total":
            line = f"Total Marks: {row['Marks']}"
        else:
            line = f"{row['Task']} - Status: {row['Status']}, Marks: {row['Marks']}"
        pdf.multi_cell(0, 10, line)
    pdf.output("/tmp/report.pdf")
    return open("/tmp/report.pdf", "rb").read()

# Employee Section
if role == "Employee":
    st.header("👨‍💼 Employee Task Entry")
    task = st.text_input("Task Name")
    desc = st.text_area("Description")
    completion = st.slider("Completion %", 0, 100, 0)
    marks = st.slider("Marks (out of 5)", 0, 5, 0)
    status = st.selectbox("Status", ["Draft", "Submitted"])
    feedback = st.text_area("Self Feedback")

    if st.button("➕ Add Task"):
        st.session_state["tasks"].append({
            "Task": task,
            "Description": desc,
            "Completion %": completion,
            "Marks": marks,
            "Status": status,
            "Self Feedback": feedback,
            "Reporting Officer Feedback": "",
            "Client Feedback": ""
        })
        st.success("✅ Task added!")

# Reporting Officer Section
elif role == "Reporting Officer":
    st.header("🧑‍💼 Reporting Officer Dashboard")
    for i, task in enumerate(st.session_state["tasks"]):
        if task["Status"] in ["Submitted", "Reviewed"]:
            st.subheader(f"{task['Task']} (Employee Marks: {task['Marks']} / 5)")
            st.caption(task["Description"])
            st.progress(task["Completion %"] / 100)
            ro_feedback = st.text_area("Reporting Officer Feedback", key=f"ro_feedback_{i}", value=task.get("Reporting Officer Feedback", ""))
            marks = st.slider("Updated Marks (out of 5)", 0, 5, task["Marks"], key=f"ro_marks_{i}")
            if st.button(f"💾 Save Feedback for {task['Task']}", key=f"ro_save_btn_{i}"):
                task["Reporting Officer Feedback"] = ro_feedback
                task["Marks"] = marks
                task["Status"] = "Reviewed"
                st.success("✅ Feedback saved!")

# Client Section
elif role == "Client":
    st.header("🧑‍💼 Client Review & Approval")
    for i, task in enumerate(st.session_state["tasks"]):
        if task["Status"] == "Reviewed":
            st.subheader(f"{task['Task']} (Marks: {task['Marks']} / 5)")
            st.caption(task["Description"])
            st.write(f"📝 Reporting Officer Feedback: {task['Reporting Officer Feedback']}")
            feedback = st.text_area("Your Feedback", key=f"client_feedback_{i}", value=task.get("Client Feedback", ""))
            status = st.selectbox("Approval", ["Reviewed", "Approved", "Rejected"], key=f"client_status_{i}")
            if st.button(f"💾 Save Feedback for {task['Task']}", key=f"client_btn_{i}"):
                task["Client Feedback"] = feedback
                task["Status"] = status
                st.success("✅ Client feedback saved!")

# Task Dashboard
st.header("📊 All Tasks Dashboard")
if st.session_state["tasks"]:
    df = pd.DataFrame(st.session_state["tasks"])
    st.dataframe(df)

    # Export buttons
    st.sidebar.header("📥 Export Report")
    export_df = df[df["Status"] != "Draft"]

    if not export_df.empty:
        total = export_df["Marks"].sum()
        export_df.loc[len(export_df.index)] = ["Total", "", "", "", "", "", "", "", total]

        csv = export_df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button("📂 Download CSV", data=csv, file_name="task_report.csv", mime="text/csv")

        pdf = generate_pdf(export_df)
        st.sidebar.download_button("📄 Download PDF", data=pdf, file_name="task_report.pdf", mime="application/pdf")
    else:
        st.sidebar.info("🚫 No completed tasks to export yet.")
else:
    st.warning("⚠️ No tasks added yet.")
