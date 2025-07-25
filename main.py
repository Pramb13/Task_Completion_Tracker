import streamlit as st
import pandas as pd
import os

# CSV path
CSV_PATH = "task_data.csv"

# Create default DataFrame if CSV doesn't exist
if not os.path.exists(CSV_PATH):
    df = pd.DataFrame(columns=[
        "Task", "Description", "User Completion", "Officer Completion",
        "Marks", "Client Approval", "Status"
    ])
    df.to_csv(CSV_PATH, index=False)

# Load data
df = pd.read_csv(CSV_PATH)

st.title("📋 Task Completion Tracker")

role = st.sidebar.selectbox("Login as", ["Employee", "Officer", "Client", "Dashboard"])

# --- EMPLOYEE PANEL ---
if role == "Employee":
    st.header("👨‍💻 Employee Panel")

    task = st.text_input("Enter Task Name")
    description = st.text_area("Task Description (optional)")
    completion = st.slider("Mark Your Completion (%)", 0, 100, 0)

    if st.button("Submit Task"):
        new_row = {
            "Task": task,
            "Description": description,
            "User Completion": completion,
            "Officer Completion": 0,
            "Marks": 0.0,
            "Client Approval": "Pending",
            "Status": "In Progress"
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(CSV_PATH, index=False)
        st.success("✅ Task submitted successfully!")
        st.experimental_rerun()

# --- OFFICER PANEL ---
elif role == "Officer":
    st.header("🕵️ Reporting Officer Panel")

    if df.empty:
        st.warning("No tasks available.")
    else:
        task_list = df["Task"].tolist()
        selected_task = st.selectbox("Select Task to Review", task_list)
        if selected_task:
            task_index = df[df["Task"] == selected_task].index[0]

            officer_completion = st.slider("Officer Completion (%)", 0, 100, int(df.loc[task_index, "Officer Completion"]))
            df.at[task_index, "Officer Completion"] = officer_completion

            marks = round((df.loc[task_index, "User Completion"] + officer_completion) / 40, 2)
            df.at[task_index, "Marks"] = marks
            df.at[task_index, "Status"] = "Finalized"

            if st.button("Submit Officer Review"):
                df.to_csv(CSV_PATH, index=False)
                st.success("✅ Officer review submitted!")
                st.experimental_rerun()

# --- CLIENT PANEL ---
elif role == "Client":
    st.header("🤝 Client Review Panel")

    pending_df = df[df["Client Approval"] == "Pending"]

    if pending_df.empty:
        st.info("🎉 No pending tasks for approval.")
    else:
        selected_task = st.selectbox("Select Task for Approval", pending_df["Task"].tolist())
        if selected_task:
            task_index = df[df["Task"] == selected_task].index[0]
            st.write("🔍 Task Info:")
            st.write(df.loc[task_index][["Task", "Description", "User Completion", "Officer Completion", "Marks"]])

            approve = st.radio("Client Approval", ["Approve", "Reject"])
            if st.button("Submit Review"):
                df.at[task_index, "Client Approval"] = approve
                df.to_csv(CSV_PATH, index=False)
                st.success(f"✅ Task {approve}d successfully!")
                st.experimental_rerun()

# --- DASHBOARD ---
elif role == "Dashboard":
    st.header("📊 Task Overview")
    st.dataframe(df)

    with st.expander("📝 Pending Client Approvals"):
        pending_df = df[df["Client Approval"] == "Pending"]
        st.dataframe(pending_df[["Task", "User Completion", "Officer Completion", "Marks", "Status"]])
