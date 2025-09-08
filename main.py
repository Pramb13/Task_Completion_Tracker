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
# Sidebar Role Selection
# ----------------------------
role = st.sidebar.selectbox("Select Role", ["Client", "Employee", "Boss"])

# ----------------------------
# CLIENT ROLE
# ----------------------------
if role == "Client":
    st.header("👨‍💼 Client Section")

    company_name = st.text_input("Enter your Company Name")

    if company_name:
        if company_name not in st.session_state["companies"]:
            st.session_state["companies"][company_name] = {}

        st.success(f"Welcome, {company_name} Client!")

        # Add Task
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

        # Show tasks
        st.subheader("📌 Current Tasks")
        for task in st.session_state["companies"][company_name].keys():
            st.write(f"🔹 {task}")

# ----------------------------
# EMPLOYEE ROLE
# ----------------------------
elif role == "Employee":
    st.header("👩‍💻 Employee Section")

    company_name = st.text_input("Enter your Company Name")

    if company_name in st.session_state["companies"]:
        tasks = st.session_state["companies"][company_name]

        if tasks:
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
            st.success("Employee updates saved ✅")
        else:
            st.warning("No tasks available for this company yet.")
    elif company_name:
        st.error("Company not found. Please ask the client to register tasks first.")

# ----------------------------
# BOSS ROLE
# ----------------------------
elif role == "Boss":
    st.header("👨‍💼 Boss Review Section")

    company_name = st.text_input("Enter your Company Name")

    if company_name in st.session_state["companies"]:
        tasks = st.session_state["companies"][company_name]

        if tasks:
            total_marks_obtained = 0
            total_marks_possible = 0

            for task, details in tasks.items():
                st.write(f"🔹 {task}: Employee entered {details['completion']}%")

                boss_adjust = st.slider(
                    f"Boss adjust % for {task}",
                    min_value=0,
                    max_value=100,
                    value=details["completion"],
                    step=5,
                    key=f"{task}_boss"
                )

                tasks[task]["boss_adjustment"] = boss_adjust

                task_marks = calculate_task_marks(boss_adjust, details["marks"])
                total_marks_obtained += task_marks
                total_marks_possible += details["marks"]

                st.write(f"✅ Adjusted Marks: {task_marks:.2f}/{details['marks']}")

            st.subheader(f"📌 Total Marks: {total_marks_obtained:.2f} / {total_marks_possible}")

            approved = st.radio("Is the work approved?", ("Yes", "No"))
            comments = st.text_area("Boss's Comments", "Enter your feedback here...")

            if st.button("Submit Review"):
                st.success("Review Submitted ✅")
                st.write(f"**Approval:** {approved}")
                st.write(f"**Comments:** {comments}")
        else:
            st.warning("No tasks available for this company.")
    elif company_name:
        st.error("Company not found. Please ask the client to register tasks first.")
