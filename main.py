import streamlit as st
import pandas as pd
import os

# File path for storing task data
DATA_FILE = "tasks.csv"

# Initialize the CSV file if it doesn't exist
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Task", "User Completion", "Boss Completion", "Marks", "Description", "Officer Completion", "Client Approval"])
    df.to_csv(DATA_FILE, index=False)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Main App
st.set_page_config(page_title="Task Completion Tracker", layout="wide")
st.title("✅ Task Completion Tracker")

# Sidebar Roles
role = st.sidebar.selectbox("Select Your Role", ["Employee", "Officer", "Client", "Dashboard"])

# Employee View
if role == "Employee":
    st.subheader("👷 Employee Task Submission")
    task_name = st.text_input("Enter Task Name")
    task_desc = st.text_area("Describe the Task")
    user_completion = st.slider("Your Completion %", 0, 100, 0)

    if st.button("Submit Task"):
        if task_name:
            new_task = {
                "Task": task_name,
                "User Completion": user_completion,
                "Boss Completion": 0,
                "Marks": 0,
                "Description": task_desc,
                "Officer Completion": 0,
                "Client Approval": "Pending"
            }

            new_df = pd.DataFrame([new_task])
            df = load_data()
            df = pd.concat([df, new_df], ignore_index=True)
            save_data(df)

            st.success(f"✅ Task '{task_name}' submitted successfully!")
            st.experimental_rerun()
        else:
            st.warning("⚠️ Please enter a task name.")

# Officer View
elif role == "Officer":
    st.subheader("🧑‍💼 Officer Review")
    df = load_data()

    for idx, row in df.iterrows():
        st.markdown(f"### Task: {row['Task']}")
        st.markdown(f"Description: {row['Description']}")
        officer_val = st.slider(f"Officer Completion for Task {row['Task']}", 0, 100, int(row['Officer Completion']), key=f"officer_{idx}")
        df.at[idx, "Officer Completion"] = officer_val

    if st.button("Save Officer Updates"):
        save_data(df)
        st.success("✅ Officer updates saved!")

# Client View
elif role == "Client":
    st.subheader("🤝 Client Approval")
    df = load_data()

    for idx, row in df.iterrows():
        st.markdown(f"### Task: {row['Task']}")
        st.markdown(f"Description: {row['Description']}")
        st.markdown(f"Employee Completion: {row['User Completion']}%")
        st.markdown(f"Officer Completion: {row['Officer Completion']}%")
        status = st.selectbox(f"Approve Task '{row['Task']}'?", ["Pending", "Approved", "Rejected"], index=["Pending", "Approved", "Rejected"].index(row['Client Approval']), key=f"client_{idx}")
        df.at[idx, "Client Approval"] = status

        # Score calculation
        try:
            avg_completion = (int(row['User Completion']) + int(row['Officer Completion'])) / 2
            df.at[idx, "Marks"] = round(avg_completion * 0.10, 2)
        except:
            df.at[idx, "Marks"] = 0

    if st.button("Save Client Feedback"):
        save_data(df)
        st.success("✅ Client decisions saved!")

# Dashboard View
elif role == "Dashboard":
    st.subheader("📊 Task Overview")
    df = load_data()

    df['Description'] = df['Description'].fillna("None")
    df['Officer Completion'] = df['Officer Completion'].fillna("None")
    df['Client Approval'] = df['Client Approval'].fillna("None")

    st.dataframe(df)

    # Filter Pending Tasks
    pending = df[df["Client Approval"] == "Pending"][["Task", "User Completion", "Officer Completion", "Marks"]]
    if not pending.empty:
        pending["Status"] = "In Progress"
        with st.expander("📌 Pending Client Approvals"):
            st.dataframe(pending)

    # Export Option
    st.download_button("📥 Download All Data", data=df.to_csv(index=False), file_name="task_data.csv", mime="text/csv")
