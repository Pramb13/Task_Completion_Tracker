import streamlit as st
import pandas as pd

st.set_page_config(page_title="Task Completion Tracker", layout="wide")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Employee", "Task", "Completion", "Status", "Marks", "Reviewed"])
if 'should_rerun' not in st.session_state:
    st.session_state.should_rerun = False

# Simulated user role selection
role = st.sidebar.selectbox("Login as", ["Employee", "Officer"])

# Employee view
if role == "Employee":
    st.title("🧑‍💻 Employee Task Submission")

    employee_name = st.text_input("Enter your name:")
    task_name = st.text_input("Task Name:")
    completion = st.slider("Completion %", 0, 100, 0)

    if st.button("Submit Task"):
        if employee_name and task_name:
            # Score logic
            marks = completion / 10

            # Save task
            new_row = {
                "Employee": employee_name,
                "Task": task_name,
                "Completion": completion,
                "Status": "Submitted",
                "Marks": marks,
                "Reviewed": "No"
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("✅ Task submitted!")
            st.session_state.should_rerun = True
        else:
            st.error("❌ Please fill in all fields.")

# Officer view
elif role == "Officer":
    st.title("🧑‍💼 Officer Review Panel")

    df = st.session_state.df
    if df.empty:
        st.info("No tasks submitted yet.")
    else:
        # Display all tasks
        st.subheader("📋 All Tasks")
        st.dataframe(df[["Employee", "Task", "Completion", "Status", "Marks", "Reviewed"]])

        # Filter pending review
        pending_df = df[df["Reviewed"] == "No"]

        if not pending_df.empty:
            st.subheader("⏳ Pending Reviews")

            for i, row in pending_df.iterrows():
                with st.expander(f"Review Task: {row['Task']} by {row['Employee']}"):
                    st.write(f"**Completion:** {row['Completion']}%")
                    st.write(f"**Auto Marks:** {row['Marks']}")

                    if st.button(f"Mark Reviewed ✅ - {i}"):
                        st.session_state.df.at[i, "Reviewed"] = "Yes"
                        st.session_state.df.at[i, "Status"] = "Reviewed"
                        st.success(f"Task '{row['Task']}' marked as Reviewed.")
                        st.session_state.should_rerun = True

        else:
            st.success("🎉 No pending reviews.")

        st.subheader("📤 Export All Data")
        csv = st.session_state.df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="task_completion_report.csv", mime="text/csv")

# Handle rerun only when necessary
if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    st.experimental_rerun()
