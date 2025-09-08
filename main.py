import streamlit as st

# ----------------------------
# Session state initialization
# ----------------------------
if "companies" not in st.session_state:
    st.session_state["companies"] = {}

# ----------------------------
# Utility function
# ----------------------------
def calculate_task_marks(completion_percentage, total_marks=5):
    return total_marks * (completion_percentage / 100)

# ----------------------------
# App Title
# ----------------------------
st.title("📊 Task Completion Tracker")

# ----------------------------
# Step 1: Client Login (Company Name)
# ----------------------------
company_name = st.text_input("Enter your Company Name")

if company_name:
    # Initialize company data if not exists
    if company_name not in st.session_state["companies"]:
        st.session_state["companies"][company_name] = {}

    st.success(f"Welcome, {company_name} Client! You can manage your tasks here.")

    # ----------------------------
    # Step 2: Add / Manage Tasks
    # ----------------------------
    st.subheader("➕ Add New Task")
    new_task = st.text_input("Task Name")
    if st.button("Add Task"):
        if new_task and new_task not in st.session_state["companies"][company_name]:
            st.session_state["companies"][company_name][new_task] = {
                "marks": 5,
                "completion": 0,
                "boss_adjustment": 0
            }
            st.success(f"Task '{new_task}' added for {company_name} ✅")
        elif new_task in st.session_state["companies"][company_name]:
            st.warning("Task already exists!")
        else:
            st.warning("Enter a valid task name!")

    tasks = st.session_state["companies"][company_name]

    if tasks:
        # ----------------------------
        # Step 3: Employee Input
        # ----------------------------
        st.header("👩‍💻 Employee Section: Enter Completion %")
        for task, details in tasks.items():
            completion = st.slider(
                f"{task} Completion",
                min_value=0,
                max_value=100,
                value=details["completion"],
                step=5,
                key=f"{task}_employee"
            )
            tasks[task]["completion"] = completion

        # ----------------------------
        # Step 4: Boss Review Section
        # ----------------------------
        st.header("👨‍💼 Boss Review and Adjustments")
        total_marks_obtained = 0
        total_marks_possible = 0

        for task, details in tasks.items():
            st.write(f"🔹 {task}: Employee entered {details['completion']}%")

            # Boss adjustment
            boss_adjust = st.slider(
                f"Boss adjust % for {task}",
                min_value=0,
                max_value=100,
                value=details["completion"],
                step=5,
                key=f"{task}_boss"
            )

            tasks[task]["boss_adjustment"] = boss_adjust

            # Recalculate marks
            task_marks = calculate_task_marks(boss_adjust, details["marks"])
            total_marks_obtained += task_marks
            total_marks_possible += details["marks"]

            st.write(f"✅ Adjusted Marks: {task_marks:.2f}/{details['marks']}")

        # ----------------------------
        # Step 5: Boss Final Review
        # ----------------------------
        st.subheader(f"📌 Total Marks Obtained: {total_marks_obtained:.2f} / {total_marks_possible}")

        approved = st.radio("Is the work approved?", ("Yes", "No"))
        comments = st.text_area("Boss's Comments", "Enter your feedback here...")

        if st.button("Submit Report"):
            st.success("Report Submitted Successfully ✅")
            st.write("### Final Review")
            st.write(f"**Approval Status:** {approved}")
            st.write(f"**Boss's Comments:** {comments}")
