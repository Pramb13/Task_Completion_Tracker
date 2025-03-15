import streamlit as st
import pandas as pd
import os

# Define file path for storing task data
data_file = "task_data.csv"

def load_data():
    """Load task data from a CSV file or initialize if not exists."""
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame({"Task": [f"Task {i+1}" for i in range(6)], "User Completion": [0]*6, "Boss Completion": [0]*6, "Marks": [0]*6})

def save_data(df):
    """Save the task data to a CSV file."""
    df.to_csv(data_file, index=False)

def calculate_marks(completion_percentage, total_marks=5):
    return total_marks * (completion_percentage / 100)

# Load existing data
df = load_data()

# User authentication
st.sidebar.header("Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Boss"])

# Title
st.title("Task Completion Tracker")

st.write("This app tracks the completion of six tasks, reviewed by the reporting boss.")

if role == "Employee":
    st.header("Enter Completion Percentages")
    for i in range(len(df)):
        df.at[i, "User Completion"] = st.slider(f'{df.at[i, "Task"]} Completion', 0, 100, int(df.at[i, "User Completion"]), 5)
    
    if st.button("Submit Completion"):
        save_data(df)
        st.success("Task completion updated successfully!")

elif role == "Boss":
    st.header("Boss Review & Adjustments")
    total_marks_obtained = 0
    for i in range(len(df)):
        st.write(f"{df.at[i, 'Task']}: {df.at[i, 'User Completion']}% completed")
        df.at[i, "Boss Completion"] = st.slider(f"Adjust completion for {df.at[i, 'Task']}:", 0, 100, int(df.at[i, "User Completion"]), 5)
        df.at[i, "Marks"] = calculate_marks(df.at[i, "Boss Completion"])
        total_marks_obtained += df.at[i, "Marks"]
        st.progress(df.at[i, "Boss Completion"] / 100)
        st.write(f"Adjusted Marks: {df.at[i, 'Marks']:.2f}")
    
    st.subheader(f"Total Marks Obtained: {total_marks_obtained:.2f} / 30")
    
    if st.button("Finalize Review"):
        save_data(df)
        st.success("Boss's review has been saved!")

st.sidebar.header("Export Report")
if st.sidebar.button("Download CSV"):
    df.to_csv("task_report.csv", index=False)
    st.sidebar.success("Report downloaded as task_report.csv")
