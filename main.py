import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# Initialize session state for tasks
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

# Function to calculate marks
def calculate_marks(completion_percentage, total_marks=5):
    return round(total_marks * (completion_percentage / 100), 2)

# Function to generate a PDF report
def generate_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Task Completion Report", ln=True, align="C")
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Task", 1, 0, "C")
    pdf.cell(40, 10, "User (%)", 1, 0, "C")
    pdf.cell(40, 10, "Officer (%)", 1, 0, "C")
    pdf.cell(40, 10, "Marks", 1, 1, "C")
    
    # Table Data
    pdf.set_font("Arial", size=12)
    if "tasks" in st.session_state and st.session_state["tasks"]:
        for task in st.session_state["tasks"]:
            pdf.cell(60, 10, task["Task"], 1, 0, "C")
            pdf.cell(40, 10, f"{task['User Completion']}%", 1, 0, "C")
            pdf.cell(40, 10, f"{task['Officer Completion']}%", 1, 0, "C")
            pdf.cell(40, 10, str(task["Marks"]), 1, 1, "C")
    
    # Generate PDF as BytesIO object
    pdf_output = io.BytesIO()
    pdf.output(pdf_output, "F")  # Writes to the buffer
    pdf_output.seek(0)  # Move to start of the buffer
    
    return pdf_output

# User authentication
st.sidebar.header("🔑 Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Reporting Officer"])

# Title
st.title("📊 Task Completion Tracker")
st.markdown("### A streamlined way to track and evaluate task progress.")

# Employee Section
if role == "Employee":
    st.header("📝 Add or Update Your Tasks")

    # Add new tasks dynamically
    new_task_name = st.text_input("Enter a new task name:")
    if st.button("➕ Add Task") and new_task_name:
        if new_task_name not in [task["Task"] for task in st.session_state["tasks"]]:
            st.session_state["tasks"].append({"Task": new_task_name, "User Completion": 0, "Officer Completion": 0, "Marks": 0})
            st.success(f"Task '{new_task_name}' added successfully!")
            st.rerun()
        else:
            st.warning("Task already exists! Please enter a different task.")

    # Update completion percentages
    if st.session_state["tasks"]:
        for task in st.session_state["tasks"]:
            task["User Completion"] = st.slider(f'📌 {task["Task"]} Completion', 0, 100, task["User Completion"], 5)

        if st.button("✅ Submit Completion"):
            st.success("Task completion updated successfully!")

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
            st.write(f"🔹 Adjusted Marks: **{task['Marks']}**")

        st.subheader(f"🏆 Total Marks Obtained: **{total_marks_obtained}**")

        if st.button("✔️ Finalize Review"):
            st.success("Reporting Officer's review has been saved!")

# Export Report Section
st.sidebar.header("📥 Export Report")

if st.session_state["tasks"]:
    df = pd.DataFrame(st.session_state["tasks"])
    
    # CSV Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button("📂 Download CSV", data=csv, file_name="task_report.csv", mime="text/csv")

    # PDF Export
    pdf_data = generate_pdf()
    st.sidebar.download_button("📄 Download PDF", data=pdf_data, file_name="task_report.pdf", mime="application/pdf")
