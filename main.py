import streamlit as st
import pandas as pd

st.set_page_config(page_title="Task Completion Tracker", layout="wide")

# Dummy tasks for employee view
tasks = [
    "Task 1: Planning and Coordination",
    "Task 2: Site Inspection",
    "Task 3: Material Management",
    "Task 4: Report Submission",
    "Task 5: Communication with Vendor",
    "Task 6: Safety Compliance",
    "Task 7: Attendance and Supervision",
    "Task 8: Documentation",
]

# Set sidebar role (fixed as Employee)
st.sidebar.title("User Role")
st.sidebar.markdown("**Role:** Employee")

st.title("📋 Task Completion Tracker (Employee View)")

# Employee fills completion % for each task
completion_data = []
for task in tasks:
    percent_complete = st.slider(f"{task}", 0, 100, 0, 5)
    completion_data.append([task, percent_complete])

# Convert to DataFrame
df = pd.DataFrame(completion_data, columns=["Task", "Completion %"])

# Display table
st.write("### Task Completion Summary")
st.dataframe(df, use_container_width=True)

# Export CSV
if st.button("📤 Export to CSV"):
    export_df = df.copy()
    
    # Total row
    total = export_df["Completion %"].sum()
    total_row = [""] * (len(export_df.columns) - 1) + [total]
    total_row[0] = "Total"
    export_df.loc[len(export_df.index)] = total_row

    # Save
    export_df.to_csv("task_completion_employee.csv", index=False)
    st.success("CSV exported successfully as `task_completion_employee.csv`")

# Optional: Download link
with open("task_completion_employee.csv", "rb") as file:
    st.download_button(
        label="⬇️ Download CSV",
        data=file,
        file_name="task_completion_employee.csv",
        mime="text/csv"
    )
