import streamlit as st
import pandas as pd

# ---------- Session State Initialization ----------
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "reviewed" not in st.session_state:
    st.session_state["reviewed"] = False
if "finalized" not in st.session_state:
    st.session_state["finalized"] = False

# ---------- Function Definitions ----------
def calculate_marks(completion_percentage, total_marks=5):
    return round(total_marks * (completion_percentage / 100), 2)

def get_status(task):
    if task["Officer Completion"] == "":
        return "Pending Review"
    elif task["Client Approval"] == "":
        return "Pending Client"
    else:
        return "Finalized"

# ---------- UI Layout ----------
st.sidebar.header("🔐 Login")
role = st.sidebar.radio("Select your role:", ["Employee", "Reporting Officer", "Client Reviewer"])

st.image("https://companieslogo.com/img/orig/GMDCLTD.NS-26174231.png?t=1720244492", width=100)
st.title("📊 Task Completion Tracker")
st.markdown("### A streamlined system to track, review, and finalize tasks.")

# ---------- Employee View ----------
if role == "Employee":
    st.header("📝 Add or Update Tasks")
    if not st.session_state["submitted"]:
        new_task = st.text_input("Enter a new task:")
        if st.button("➕ Add Task") and new_task:
            if len(st.session_state["tasks"]) < 6:
                st.session_state["tasks"].append({
                    "Task": new_task,
                    "User Completion": 0,
                    "Officer Completion": "",
                    "Marks": 0,
                    "Client Approval": "",
                })
                st.success(f"✅ Task '{new_task}' added!")
                st.rerun()

    for i, task in enumerate(st.session_state["tasks"]):
        if st.session_state["submitted"]:
            st.write(f"📌 **{task['Task']}** - Submitted: {task['User Completion']}%")
        else:
            st.session_state["tasks"][i]["User Completion"] = st.slider(
                f"📌 {task['Task']} Completion", 0, 100,
                task["User Completion"], 5, key=f"user_{i}"
            )

    if not st.session_state["submitted"]:
        if st.button("✅ Submit Tasks"):
            st.session_state["submitted"] = True
            st.success("✅ Tasks submitted! Waiting for review.")

# ---------- Reporting Officer View ----------
elif role == "Reporting Officer":
    st.header("📋 Review Employee Tasks")
    if not st.session_state["submitted"]:
        st.warning("⚠️ No tasks submitted by employee yet.")
    else:
        total_marks = 0
        for i, task in enumerate(st.session_state["tasks"]):
            st.write(f"📌 **{task['Task']}** - Employee: {task['User Completion']}%")

            if task["Officer Completion"] == "":
                task["Officer Completion"] = task["User Completion"]

            st.session_state["tasks"][i]["Officer Completion"] = st.slider(
                f"Adjust Completion: {task['Task']}", 0, 100,
                int(task["Officer Completion"]), 5, key=f"officer_{i}"
            )

            marks = calculate_marks(task["Officer Completion"])
            st.session_state["tasks"][i]["Marks"] = marks
            total_marks += marks
            st.progress(task["Officer Completion"] / 100)
            st.write(f"🔹 Marks Given: **{marks}/5**")

        st.subheader(f"🏆 Total Marks: {round(total_marks, 2)} / 30")

        if st.button("✔️ Finalize Officer Review"):
            st.session_state["reviewed"] = True
            st.success("✅ Officer review completed and saved!")

# ---------- Client Reviewer View ----------
elif role == "Client Reviewer":
    st.header("🧾 Client Task Verification")
    if not st.session_state["reviewed"]:
        st.warning("⚠️ Officer review is not yet finalized.")
    else:
        for i, task in enumerate(st.session_state["tasks"]):
            st.write(f"📌 **{task['Task']}** - Officer: {task['Officer Completion']}% - Marks: {task['Marks']}")

            if task["Client Approval"] == "":
                approval = st.radio(
                    f"Approve Task: {task['Task']}", ["Pending", "Approved", "Rejected"],
                    key=f"client_{i}", index=0
                )
                st.session_state["tasks"][i]["Client Approval"] = approval

        if st.button("✅ Finalize Client Review"):
            st.session_state["finalized"] = True
            st.success("🎉 All tasks reviewed by client!")

# ---------- Dashboard ----------
st.sidebar.header("📊 Task Dashboard")
if st.session_state["tasks"]:
    df = pd.DataFrame(st.session_state["tasks"])
    df["Status"] = df.apply(get_status, axis=1)

    st.subheader("📌 Task Overview")
    st.dataframe(df[["Task", "User Completion", "Officer Completion", "Marks", "Client Approval", "Status"]])

    pending = df[df["Status"] != "Finalized"]
    if not pending.empty:
        st.warning("⏳ Pending Tasks for Review or Approval")
        st.dataframe(pending[["Task", "Status"]])

    # Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button("📥 Download Report", data=csv, file_name="final_task_report.csv", mime="text/csv")
else:
    st.sidebar.info("No tasks available.")
