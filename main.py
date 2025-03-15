import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# Initialize session state for tasks
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

# Function to calculate marks
def calculate_marks(completion_percentage, total_marks=5):
    return total_marks * (completion_percentage / 100)

# Sidebar with user authentication
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/747/747376.png", width=100)  # Profile icon
st.sidebar.header("🔑 Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Reporting Officer"], index=0)

# Title with styled heading
st.markdown(
    "<h1 style='text-align: center; color: #4A90E2;'>📊 Task Completion Tracker</h1>",
    unsafe_allow_html=True,
)
st.markdown("<hr>", unsafe_allow_html=True)

if role == "Employee":
    st.subheader("➕ Add or Update Your Tasks")

    # Task Input with Icon
    new_task_name = st.text_input("📌 Enter a new task name:")
    if st.button("➕ Add Task", use_container_width=True) and new_task_name:
        if new_task_name not in [task["Task"] for task in st.session_state["tasks"]]:
            st.session_state["tasks"].append({"Task": new_task_name, "User Completion": 0, "Officer Completion": 0, "Marks": 0})
            st.success(f"✅ Task '{new_task_name}' added successfully!")
            st.rerun()
        else:
            st.warning("⚠ Task already exists! Please enter a different task.")

    # Update Completion Status
    if st.session_state["tasks"]:
        st.subheader("📌 Update Task Completion")
        for task in st.session_state["tasks"]:
            task["User Completion"] = st.slider(f"**{task['Task']} Completion**", 0, 100, task["User Completion"], 5)
            st.progress(task["User Completion"] / 100)

        if st.button("✔ Submit Completion", use_container_width=True):
            st.success("✅ Task completion updated successfully!")

elif role == "Reporting Officer":
    st.subheader("📝 Review & Adjust Task Completion")

    total_marks_obtained = 0
    if st.session_state["tasks"]:
        for task in st.session_state["tasks"]:
            st.markdown(f"**📌 {task['Task']}** - Employee Completion: **{task['User Completion']}%**")
            task["Officer Completion"] = st.slider(f"🔧 Adjust Completion for {task['Task']}", 0, 100, task["User Completion"], 5)
            task["Marks"] = calculate_marks(task["Officer Completion"])
            total_marks_obtained += task["Marks"]
            st.progress(task["Officer Completion"] / 100)
            st.write(f"🎯 Adjusted Marks: **{task['Marks']:.2f}**")

        st.subheader(f"🏆 Total Marks Obtained: **{total_marks_obtained:.2f}**")

        if st.button("📌 Finalize Review", use_container_width=True):
            st.success("✅ Reporting Officer's review has been saved!")

# Export Report Section
st.sidebar.header("📄 Export Report")
if st.session_state["tasks"]:
    df = pd.DataFrame(st.session_state["tasks"])
    
    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="task_report.csv",
        mime="text/csv",
    )

    # Function to create PDF
    def generate_pdf():
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, "Task Completion Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.cell(50, 10, "Task", border=1)
        pdf.cell(50, 10, "Employee Completion", border=1)
        pdf.cell(50, 10, "Officer Completion", border=1)
        pdf.cell(30, 10, "Marks", border=1)
        pdf.ln()

        for task in st.session_state["tasks"]:
            pdf.cell(50, 10, task["Task"], border=1)
            pdf.cell(50, 10, f"{task['User Completion']}%", border=1)
            pdf.cell(50, 10, f"{task['Officer Completion']}%", border=1)
            pdf.cell(30, 10, f"{task['Marks']:.2f}", border=1)
            pdf.ln()

        pdf_output = io.BytesIO()
        pdf.output(pdf_output, "F")
        return pdf_output.getvalue()

    # Download PDF
    pdf_data = generate_pdf()
    st.sidebar.download_button(
        label="📥 Download PDF",
        data=pdf_data,
        file_name="task_report.pdf",
        mime="application/pdf",
    )
