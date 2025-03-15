import streamlit as st
import pandas as pd
import os

# Define file path for storing task data
data_file = "task_data.csv"

def load_data():
    """Load task data from a CSV file or initialize an empty DataFrame."""
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=["Task", "User Completion", "Boss Completion", "Marks"])

def save_data(df):
    """Save the task data to a CSV file."""
    df.to_csv(data_file, index=False)

def calculate_marks(completion_percentage, total_marks=5):
    return total_marks * (completion_percentage / 100)

# Load existing data
df = load_data()

# User authentication
st.sidebar.header("Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Reporting Officer"])

# Title
st.title("Task Completion Tracker")
st.write("This app tracks task completion reviewed by the Reporting Officer.")

if role == "Employee":
    st.header("Add or Update Your Tasks")

    # Add new tasks dynamically
    new_task_name = st.text_input("Enter a new task name:")
    if st.button("Add Task") and new_task_name:
        if new_task_name not in df["Task"].values:
            new_task = pd.DataFrame({"Task": [new_task_name], "User Completion": [0], "Boss Completion": [0], "Marks": [0]})
            df = pd.concat([df, new_task], ignore_index=True)
            save_data(df)
            st.success(f"Task '{new_task_name}' added successfully!")
            st.rerun()  # Refresh the page to show the new task
        else:
            st.warning("Task already exists! Please enter a different task.")

    # Update completion percentages
    if not df.empty:
        for i in range(len(df)):
            df.at[i, "User Completion"] = st.slider(f'{df.at[i, "Task"]} Completion', 0, 100, int(df.at[i, "User Completion"]), 5)

        if st.button("Submit Completion"):
            save_data(df)
            st.success("Task completion updated successfully!")

elif role == "Reporting Officer":
    st.header("Boss Review & Adjustments")
    total_marks_obtained = 0

    if not df.empty:
        for i in range(len(df)):
            st.write(f"**{df.at[i, 'Task']}**: {df.at[i, 'User Completion']}% completed")
            df.at[i, "Boss Completion"] = st.slider(f"Adjust completion for {df.at[i, 'Task']}", 0, 100, int(df.at[i, "User Completion"]), 5)
            df.at[i, "Marks"] = calculate_marks(df.at[i, "Boss Completion"])
            total_marks_obtained += df.at[i, "Marks"]
            st.progress(df.at[i, "Boss Completion"] / 100)
            st.write(f"Adjusted Marks: {df.at[i, 'Marks']:.2f}")

        st.subheader(f"Total Marks Obtained: {total_marks_obtained:.2f}")

        if st.button("Finalize Review"):
            save_data(df)
            st.success("Boss's review has been saved!")

# Export Report Section
st.sidebar.header("Export Report")

# Convert DataFrame to CSV for download
csv = df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="Download CSV",
    data=csv,
    file_name="task_report.csv",
    mime="text/csv",
)
