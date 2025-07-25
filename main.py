import streamlit as st
import json
import pandas as pd
import os

# ---------- Load Users from JSON ----------
@st.cache_data
def load_users():
    with open("users.json") as f:
        return json.load(f)

# ---------- Authenticate ----------
def authenticate(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return True, users[username]["role"]
    return False, None

# ---------- Save task progress ----------
def save_task(username, progress):
    df = pd.DataFrame([{"username": username, "task_progress": progress}])
    if os.path.exists("employee_tasks.csv"):
        existing = pd.read_csv("employee_tasks.csv")
        existing = existing[existing["username"] != username]
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv("employee_tasks.csv", index=False)

# ---------- Save officer review ----------
def save_score(officer, employee, score):
    df = pd.DataFrame([{"officer": officer, "employee": employee, "score": score}])
    if os.path.exists("officer_scores.csv"):
        existing = pd.read_csv("officer_scores.csv")
        existing = existing[(existing["officer"] != officer) | (existing["employee"] != employee)]
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv("officer_scores.csv", index=False)

# ---------- Save client review ----------
def save_review(client, feedback):
    df = pd.DataFrame([{"client": client, "feedback": feedback}])
    if os.path.exists("client_feedback.csv"):
        existing = pd.read_csv("client_feedback.csv")
        existing = pd.concat([existing, df], ignore_index=True)
    else:
        existing = df
    existing.to_csv("client_feedback.csv", index=False)

# ---------- Login Page ----------
def login():
    st.title("🔐 Task Completion Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        authenticated, role = authenticate(username, password)
        if authenticated:
            st.session_state["username"] = username
            st.session_state["role"] = role
            st.success(f"Welcome {username} ({role})")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# ---------- Employee Interface ----------
def employee_page():
    st.header("🧑‍💼 Employee Task Completion")
    progress = st.slider("Select your task completion %", 0, 100, 50)
    if st.button("Submit Progress"):
        save_task(st.session_state["username"], progress)
        st.success("✅ Task progress submitted successfully!")

# ---------- Reporting Officer Interface ----------
def officer_page():
    st.header("🕵️ Reporting Officer - Review Tasks")
    if os.path.exists("employee_tasks.csv"):
        data = pd.read_csv("employee_tasks.csv")
        for _, row in data.iterrows():
            st.subheader(f"Employee: {row['username']}")
            st.write(f"Task Completion: {row['task_progress']}%")
            score = st.slider(f"Score for {row['username']}", 0, 100, key=row['username'])
            if st.button(f"Submit Score for {row['username']}", key="btn_"+row['username']):
                save_score(st.session_state["username"], row['username'], score)
                st.success(f"✅ Score submitted for {row['username']}")
    else:
        st.info("No employee task submissions found.")

# ---------- Client Interface ----------
def client_page():
    st.header("📢 Client Feedback")
    feedback = st.text_area("Your Review/Feedback")
    if st.button("Submit Feedback"):
        save_review(st.session_state["username"], feedback)
        st.success("✅ Feedback submitted successfully!")

# ---------- Admin Interface ----------
def admin_page():
    st.header("📊 Admin Dashboard")

    if os.path.exists("employee_tasks.csv"):
        st.subheader("📄 Employee Task Progress")
        df = pd.read_csv("employee_tasks.csv")
        st.dataframe(df)
    else:
        st.info("No employee data available.")

    if os.path.exists("officer_scores.csv"):
        st.subheader("📋 Officer Reviews")
        df2 = pd.read_csv("officer_scores.csv")
        st.dataframe(df2)
    else:
        st.info("No officer scores available.")

    if os.path.exists("client_feedback.csv"):
        st.subheader("🗣️ Client Feedback")
        df3 = pd.read_csv("client_feedback.csv")
        st.dataframe(df3)
    else:
        st.info("No client feedback available.")

# ---------- Main App ----------
def main():
    if "username" not in st.session_state:
        login()
    else:
        st.sidebar.title("Navigation")
        st.sidebar.write(f"👤 {st.session_state['username']} ({st.session_state['role']})")

        role = st.session_state["role"]
        if role == "Employee":
            employee_page()
        elif role == "Reporting Officer":
            officer_page()
        elif role == "Client":
            client_page()
        elif role == "Dashboard":
            admin_page()

        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.experimental_rerun()

if __name__ == "__main__":
    main()
