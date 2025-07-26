import streamlit as st
import pandas as pd

st.set_page_config(page_title="Task Completion Tracker", layout="wide")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Employee", "Task", "Description", "Completion", "Status", "Marks", "Reviewed"])
if 'should_rerun' not in st.session_state:
    st.session_state.should_rerun = False

# Simulated user role selection
role = st.sidebar.selectbox("Login as", ["Employee", "Officer"])

# ------------------------- EMPLOYEE -------------------------
if role == "Employee":
    st.title("🧑‍💻 Employee Task Submission")

    employee_name = st.text_input("Enter your name:")
    task_name = st.text_input("Task Title:")
    task_description = st.text_area("Task Description:")
    completion = st.slider("Completion Percentage (%)", 0, 100, 0)

    if st.button("Submit Task"):
        if employee_name and task_name and task_description:
            marks = completion / 10

            new_row = {
                "Employee": employee_name,
                "Task": task_name,
                "Description": task_description,
                "Completion": completion,
                "Status": "Submitted",
                "Marks": marks,
                "Reviewed": "No"
            }

            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("✅ Task submitted successfully.")
            st.session_state.should_rerun = True
        else:
            st.error("❌ Please fill in all fields.")

# ------------------------- OFFICER -------------------------
elif role == "Officer":
    st.title("🧑‍💼 Officer Review Panel")

    df = st.session_state.df
    if df.empty:
        st.info("No tasks submitted yet.")
    else:
        st.subheader("📋 All Tasks")
        st.dataframe(df[["Employee", "Task", "Description", "Completion", "Status", "Marks", "Reviewed"]])

        # Pending reviews
        pending_df = df[df["Reviewed"] == "No"]

        if not pending_df.empty:
            st.subheader("⏳ Pending Reviews")

            for i, row in pending_df.iterrows():
                with st.expander(f"Review Task: {row['Task']} by {row['Employee']}"):
                    st.markdown(f"**Description:** {row['Description']}")
                    st.markdown(f"**Completion:** {row['Completion']}%")
                    st.markdown(f"**Auto Marks:** {row['Marks']}")

                    if st.button(f"✅ Mark Reviewed - ID {i}"):
                        st.session_state.df.at[i, "Reviewed"] = "Yes"
                        st.session_state.df.at[i, "Status"] = "Reviewed"
                        st.success(f"✅ Task '{row['Task']}' marked as Reviewed.")
                        st.session_state.should_rerun = True
        else:
            st.success("🎉 No pending tasks for review.")

        # Export
        st.subheader("📤 Export All Tasks")
        csv = st.session_state.df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="task_completion_report.csv", mime="text/csv")

# ------------------------- RERUN IF NEEDED -------------------------
if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    st.experimental_rerun()
