import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Smart Task Tracker", layout="wide")

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=["Company", "Employee", "Task", "Description", "Completion", "Marks", "Status", "Reviewed", "Comments"]
    )

# Function to calculate marks
def calculate_marks(completion, total=5):
    return round((completion / 100) * total, 2)

# Role selection
role = st.sidebar.selectbox("Login as", ["Employee", "Boss"])

# ------------------------ EMPLOYEE ------------------------ #
if role == "Employee":
    st.title("🧑‍💻 Employee Task Submission")

    company = st.text_input("🏢 Enter Company Name")
    employee = st.text_input("👤 Enter Employee Name")
    task = st.text_input("📝 Task Title")
    description = st.text_area("🗒️ Task Description")
    completion = st.slider("✅ Completion Percentage (%)", 0, 100, 0)

    if st.button("📩 Submit Task"):
        if company and employee and task and description:
            marks = calculate_marks(completion)
            new_row = {
                "Company": company,
                "Employee": employee,
                "Task": task,
                "Description": description,
                "Completion": completion,
                "Marks": marks,
                "Status": "Submitted",
                "Reviewed": "No",
                "Comments": "",
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("✅ Task submitted successfully!")
        else:
            st.error("❌ Please fill all fields!")

# ------------------------ BOSS ------------------------ #
elif role == "Boss":
    st.title("🧑‍💼 Boss Dashboard")

    company_name = st.text_input("🏢 Enter your Company Name to View Tasks")

    if not company_name:
        st.info("ℹ️ Please enter your company name to see tasks.")
    else:
        company_df = st.session_state.df[st.session_state.df["Company"] == company_name]

        if company_df.empty:
            st.info("ℹ️ No tasks submitted yet for this company.")
        else:
            st.subheader(f"📋 All Tasks for {company_name}")
            st.dataframe(company_df)

            st.subheader("⏳ Pending Reviews")
            pending_df = company_df[company_df["Reviewed"] == "No"]

            if not pending_df.empty:
                for i, row in pending_df.iterrows():
                    with st.expander(f"Review Task: {row['Task']} by {row['Employee']}"):
                        st.markdown(f"**Description:** {row['Description']}")
                        st.markdown(f"**Reported Completion:** {row['Completion']}%")
                        st.markdown(f"**Auto Marks:** {row['Marks']}")

                        # Boss adjustment
                        adjusted = st.slider(
                            f"Boss adjust completion % for {row['Task']}",
                            0, 100, int(row["Completion"])
                        )
                        adjusted_marks = calculate_marks(adjusted)
                        st.write(f"📊 Adjusted Marks: {adjusted_marks}")

                        # Approval or rejection
                        approved = st.radio("Approve this task?", ["Yes", "No"], key=f"approve_{i}")
                        comments = st.text_area("Boss's Comments", key=f"comment_{i}")

                        if st.button(f"✅ Finalize Review for Task ID {i}"):
                            st.session_state.df.at[i, "Completion"] = adjusted
                            st.session_state.df.at[i, "Marks"] = adjusted_marks
                            st.session_state.df.at[i, "Reviewed"] = "Yes"
                            st.session_state.df.at[i, "Status"] = "Approved" if approved == "Yes" else "Rejected"
                            st.session_state.df.at[i, "Comments"] = comments
                            st.success(f"✅ Task '{row['Task']}' reviewed successfully!")

            else:
                st.success("🎉 All tasks have been reviewed for this company.")

            # Export option
            st.subheader("📤 Export to CSV")
            csv = company_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Company Task Data", csv, f"{company_name}_tasks.csv", "text/csv"
            )
