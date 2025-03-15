import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def calculate_marks(completion_percentage, total_marks=5):
    return total_marks * (completion_percentage / 100)

def generate_pdf(df):
    """Generate a PDF report of the task data."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Task Completion Report")
    pdf.drawString(100, 750, "Task Completion Report")
    pdf.drawString(100, 730, "-" * 40)
    y_position = 710
    for i, row in df.iterrows():
        officer_completion = row.get('Officer Completion', 0)
        marks = row.get('Marks', 0)
        pdf.drawString(100, y_position, f"{row['Task']}: {officer_completion}% completed, Marks: {marks:.2f}")
        y_position -= 20
    pdf.save()
    buffer.seek(0)
    return buffer

# Initialize session state for task storage
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

df = pd.DataFrame(st.session_state["tasks"], columns=["Task", "User Completion", "Officer Completion", "Marks"])

# User authentication
st.sidebar.header("Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Reporting Officer"])

# Title
st.title("Task Completion Tracker")
st.write("This app tracks task completion reviewed by the Reporting Officer.")

if role == "Employee":
    if "tasks_added" not in st.session_state:
        st.session_state["tasks_added"] = False
    
    if not st.session_state["tasks_added"]:
        st.header("Add New Tasks")
        num_tasks = st.number_input("How many tasks do you want to add?", min_value=1, step=1)
        new_tasks = []
        for i in range(int(num_tasks)):
            task_name = st.text_input(f"Enter name for Task {i+1}", key=f"task_{i}")
            if task_name:
                new_tasks.append({"Task": task_name, "User Completion": 0, "Officer Completion": 0, "Marks": 0})
        
        if st.button("Add Tasks") and new_tasks:
            st.session_state["tasks"].extend(new_tasks)
            st.session_state["tasks_added"] = True
            st.rerun()
    else:
        st.header("Enter Completion Percentages")
        for i in range(len(st.session_state["tasks"])):
            st.write(f"**{st.session_state['tasks'][i]['Task']}**")
            st.session_state["tasks"][i]["User Completion"] = st.slider(f'{st.session_state["tasks"][i]["Task"]} Completion', 0, 100, int(st.session_state["tasks"][i]["User Completion"]), 5)
        
        if st.button("Submit Completion"):
            st.success("Task completion updated successfully!")

elif role == "Reporting Officer":
    st.header("Reporting Officer Review & Adjustments")
    total_marks_obtained = 0
    for i in range(len(st.session_state["tasks"])):
        st.write(f"**{st.session_state['tasks'][i]['Task']}**: {st.session_state['tasks'][i]['User Completion']}% completed")
        st.session_state["tasks"][i]["Officer Completion"] = st.slider(f"Adjust completion for {st.session_state['tasks'][i]['Task']}", 0, 100, int(st.session_state["tasks"][i]["User Completion"]), 5)
        st.session_state["tasks"][i]["Marks"] = calculate_marks(st.session_state["tasks"][i]["Officer Completion"])
        total_marks_obtained += st.session_state["tasks"][i]["Marks"]
        st.progress(st.session_state["tasks"][i]["Officer Completion"] / 100)
        st.write(f"Adjusted Marks: {st.session_state['tasks'][i]['Marks']:.2f}")
    
    st.subheader(f"Total Marks Obtained: {total_marks_obtained:.2f}")
    if st.button("Finalize Review"):
        st.success("Reporting Officer's review has been saved!")

# Export Report with Download Buttons
st.sidebar.header("Export Report")

# Convert session state data to DataFrame for export
export_df = pd.DataFrame(st.session_state["tasks"], columns=["Task", "User Completion", "Officer Completion", "Marks"])

# CSV Download
csv = export_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Download CSV",
    data=csv,
    file_name="task_report.csv",
    mime="text/csv",
)

# PDF Download
pdf_buffer = generate_pdf(export_df)
st.sidebar.download_button(
    label="Download PDF",
    data=pdf_buffer,
    file_name="task_report.pdf",
    mime="application/pdf",
)
