import streamlit as st
import pandas as pd
import json
import os

# ------------------ Load Tasks ------------------ #
def load_tasks():
    if os.path.exists("data.csv"):
        return pd.read_csv("data.csv")
    return pd.DataFrame(columns=["Task", "Description", "Status", "Score", "Review", "AssignedTo", "SubmittedBy"])

# ------------------ Save Tasks ------------------ #
def save_tasks(df):
    df.to_csv("data.csv", index=False)

# ------------------ Employee View ------------------ #
def employee_view():
    st.header("👨‍💼 Employee Dashboard")
    df = load_tasks()

    with st.form("add_task_form"):
        st.subheader("➕ Add Task")
        submitted_by = st.text_input("Your Name")
        task = st.text_input("Task Title")
        desc = st.text_area("Description")
        submitted = st.form_submit_button("Submit Task")

        if submitted and task and submitted_by:
            new_row = {
                "Task": task,
                "Description": desc,
                "Status": "Draft",
                "Score": "",
                "Review": "",
                "AssignedTo": "",
                "SubmittedBy": submitted_by
            }
            df = df._append(new_row, ignore_index=True)
            save_tasks(df)
            st.success("✅ Task submitted!")

    st.subheader("📄 All Tasks by Employees")
    st.dataframe(df[df["Status"] == "Draft"])

# ------------------ Reporting Officer View ------------------ #
def ro_view():
    st.header("🧑‍💼 Reporting Officer Dashboard")
    df = load_tasks()

    for i, row in df.iterrows():
        if row["Status"] == "Draft":
            with st.expander(f"📝 Task: {row['Task']} by {row['SubmittedBy']}"):
                st.write("📄", row["Description"])
                score = st.slider("Completion Score", 0, 100, step=10, key=f"score_{i}")
                if st.button("✔️ Submit Score", key=f"btn_{i}"):
                    df.at[i, "Score"] = score
                    df.at[i, "Status"] = "Completed"
                    save_tasks(df)
                    st.success("Score submitted ✅")

    st.subheader("✅ All Reviewed Tasks")
    st.dataframe(df[df["Status"] == "Completed"])

# ------------------ Client View ------------------ #
def client_view():
    st.header("🤝 Client Dashboard")
    df = load_tasks()

    for i, row in df.iterrows():
        if row["Status"] == "Completed" and not row["Review"]:
            with st.expander(f"📦 {row['Task']} - Score: {row['Score']}"):
                st.write(row["Description"])
                review = st.text_area("Client Review", key=f"review_{i}")
                if st.button("📨 Submit Review", key=f"rev_btn_{i}"):
                    df.at[i, "Review"] = review
                    save_tasks(df)
                    st.success("Review submitted ✅")

    st.subheader("🔍 All Tasks with Reviews")
    st.dataframe(df[df["Review"] != ""])

# ------------------ Sidebar Role Selection ------------------ #
st.set_page_config(page_title="Task Completion Tracker", layout="centered")
st.title("📋 Task Completion Tracker")

st.sidebar.title("Select Role")
role = st.sidebar.radio("Choose your role:", ["Employee", "Reporting Officer", "Client"])

# ------------------ View Rendering ------------------ #
if role == "Employee":
    employee_view()
elif role == "Reporting Officer":
    ro_view()
elif role == "Client":
    client_view()
