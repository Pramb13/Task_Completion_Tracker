import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Task Completion Tracker", layout="wide")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Employee", "Task", "Description", "Completion", "Status", "Marks", "Reviewed"])

# User login role
role = st.sidebar.selectbox("Login as", ["Employee", "Officer", "Client"])

# ------------------------ EMPLOYEE ------------------------ #
if role == "Employee":
    st.title("🧑‍💻 Employee Task Submission")

    employee_name = st.text_input("👤 Enter your name")
    task_title = st.text_input("📝 Task Title")
    task_description = st.text_area("🗒️ Task Description")
    completion = st.slider("✅ Completion Percentage (%)", 0, 100, 0)

    if st.button("📩 Submit Task"):
        if employee_name and task_title and task_description:
            marks = round(completion / 10, 2)
            new_row = {
                "Employee": employee_name,
                "Task": task_title,
                "Description": task_description,
                "Completion": completion,
                "Status": "Submitted",
                "Marks": marks,
                "Reviewed": "No"
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("✅ Task submitted successfully!")
        else:
            st.error("❌ Please fill all fields!")

# ------------------------ OFFICER ------------------------ #
elif role == "Officer":
    st.title("🧑‍💼 Officer Dashboard")

    if st.session_state.df.empty:
        st.info("ℹ️ No tasks submitted yet.")
    else:
        st.subheader("📋 All Tasks")
        st.dataframe(st.session_state.df)

        st.subheader("⏳ Pending Reviews")
        pending_df = st.session_state.df[st.session_state.df["Reviewed"] == "No"]

        if not pending_df.empty:
            for i, row in pending_df.iterrows():
                with st.expander(f"Review Task: {row['Task']} by {row['Employee']}"):
                    st.markdown(f"**Description:** {row['Description']}")
                    st.markdown(f"**Completion:** {row['Completion']}%")
                    st.markdown(f"**Auto Marks:** {row['Marks']}")

                    if st.button(f"✅ Approve Task ID {i}"):
                        st.session_state.df.at[i, "Reviewed"] = "Yes"
                        st.session_state.df.at[i, "Status"] = "Reviewed"
                        st.success("✅ Task approved!")

        else:
            st.success("🎉 All tasks have been reviewed.")

        st.subheader("📤 Export to CSV")
        csv = st.session_state.df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "task_data.csv", "text/csv")

# ------------------------ CLIENT ------------------------ #
elif role == "Client":
    st.title("👨‍💼 Client Dashboard")

    if st.session_state.df.empty:
        st.info("ℹ️ No tasks available yet.")
    else:
        st.subheader("✅ Reviewed Tasks (Final View)")
        reviewed_df = st.session_state.df[st.session_state.df["Reviewed"] == "Yes"]
        
        if reviewed_df.empty:
            st.warning("⚠️ No reviewed tasks available yet.")
        else:
            st.dataframe(reviewed_df)

            # Summary stats
            st.subheader("📊 Project Summary")
            avg_completion = reviewed_df["Completion"].mean()
            total_tasks = len(reviewed_df)
            avg_marks = reviewed_df["Marks"].mean()

            st.metric("Total Reviewed Tasks", total_tasks)
            st.metric("Average Completion (%)", f"{avg_completion:.2f}")
            st.metric("Average Marks", f"{avg_marks:.2f}")
