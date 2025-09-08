# app.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import joblib
import os
import uuid
from datetime import datetime

st.set_page_config(page_title="IntelliScore - AI Task Evaluation", layout="wide")
st.title("IntelliScore — AI-Driven Task Evaluation (Linear Regression Only)")

# ---------------------------
# Session-state initialization
# ---------------------------
if "tasks_df" not in st.session_state:
    st.session_state.tasks_df = pd.DataFrame(columns=[
        "TaskID", "Company", "Employee", "TaskTitle", "Description",
        "EmployeeCompletion", "BossAdjusted", "Marks", "Status", "BossComments", "Timestamp"
    ])

MODEL_PATH = "linear_marks_model.pkl"

# ---------------------------
# Simple keyword sentiment (no external libs)
# ---------------------------
POS_WORDS = {"good", "great", "excellent", "well", "nice", "done", "complete", "satisfactory", "improved"}
NEG_WORDS = {"bad", "poor", "incomplete", "issue", "problem", "delay", "unsatisfactory", "fail", "late"}

def simple_sentiment(text: str) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return "neutral"
    txt = text.lower()
    pos = sum(word in txt for word in POS_WORDS)
    neg = sum(word in txt for word in NEG_WORDS)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"

# ---------------------------
# Utility functions
# ---------------------------
def marks_from_percentage(pct, task_total=5.0):
    return round((pct / 100.0) * task_total, 2)

def save_model(model):
    joblib.dump(model, MODEL_PATH)

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def train_linear_model(df):
    """Train Linear Regression on rows where BossAdjusted exists."""
    df_train = df.dropna(subset=["EmployeeCompletion", "BossAdjusted"])
    if len(df_train) < 3:
        return None, None  # not enough data
    X = df_train[["EmployeeCompletion"]].values
    y = df_train["BossAdjusted"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    rmse = mean_squared_error(y_test, preds, squared=False)
    r2 = r2_score(y_test, preds)
    # save model
    save_model(model)
    return model, {"rmse": rmse, "r2": r2, "trained_on": len(df_train)}

# ---------------------------
# Sidebar: login & role
# ---------------------------
st.sidebar.header("Login / Context")
role = st.sidebar.selectbox("Role", ["Employee", "Boss", "Client", "Admin"])
company = st.sidebar.text_input("Company Name").strip()
user = st.sidebar.text_input("Your Name").strip()

if company == "" or user == "":
    st.sidebar.warning("Enter Company Name and Your Name to continue.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.write("Model file:", MODEL_PATH)
if os.path.exists(MODEL_PATH):
    st.sidebar.success("Saved Linear Regression model found.")
else:
    st.sidebar.info("No saved model yet. Model will be trained when enough reviewed data exists.")

# ---------------------------
# Admin: quick actions
# ---------------------------
if role == "Admin":
    st.header("Admin Panel")
    st.write("You can inspect data, retrain model manually, or reset data (session only).")
    st.dataframe(st.session_state.tasks_df)
    if st.button("Retrain Model Now"):
        model, metrics = train_linear_model(st.session_state.tasks_df)
        if model is None:
            st.warning("Not enough reviewed data to train (need at least 3 reviewed entries).")
        else:
            st.success(f"Model trained. RMSE: {metrics['rmse']:.3f}, R²: {metrics['r2']:.3f}, rows used: {metrics['trained_on']}")
    if st.button("Reset All Data (session)"):
        st.session_state.tasks_df = st.session_state.tasks_df.iloc[0:0]
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        st.experimental_rerun()
    st.stop()

# ---------------------------
# Load model if exists
# ---------------------------
model = load_model()

# ---------------------------
# Employee view
# ---------------------------
if role == "Employee":
    st.header(f"Employee Panel — {company} — {user}")
    with st.form("submit_task_form", clear_on_submit=True):
        st.subheader("Submit a Task")
        title = st.text_input("Task Title")
        desc = st.text_area("Task Description")
        emp_pct = st.slider("Your Completion Percentage (%)", 0, 100, 0)
        submitted = st.form_submit_button("Submit Task")
        if submitted:
            if not title or not desc:
                st.error("Please provide both title and description.")
            else:
                tid = str(uuid.uuid4())
                row = {
                    "TaskID": tid,
                    "Company": company,
                    "Employee": user,
                    "TaskTitle": title,
                    "Description": desc,
                    "EmployeeCompletion": emp_pct,
                    "BossAdjusted": np.nan,
                    "Marks": np.nan,
                    "Status": "Submitted",
                    "BossComments": "",
                    "Timestamp": datetime.now().isoformat()
                }
                st.session_state.tasks_df = pd.concat([st.session_state.tasks_df, pd.DataFrame([row])], ignore_index=True)
                st.success("Task submitted successfully. Waiting for boss review.")

    st.subheader("Your Submitted Tasks")
    my_tasks = st.session_state.tasks_df[
        (st.session_state.tasks_df["Company"] == company) &
        (st.session_state.tasks_df["Employee"] == user)
    ].sort_values("Timestamp", ascending=False)
    st.dataframe(my_tasks.reset_index(drop=True))

# ---------------------------
# Boss view
# ---------------------------
elif role == "Boss":
    st.header(f"Boss Panel — {company} — {user}")
    st.write("Review tasks submitted for your company below. You can use AI suggestion or set completion manually.")

    # filter company tasks
    comp_tasks = st.session_state.tasks_df[st.session_state.tasks_df["Company"] == company].reset_index(drop=True)
    if comp_tasks.empty:
        st.info("No tasks submitted for your company yet.")
    else:
        st.write(f"Total tasks for {company}: {len(comp_tasks)}")
        # Show training metrics if model exists
        if model is not None:
            st.info("A saved Linear Regression model is available for suggestions.")
        else:
            st.info("No trained model available yet. As boss reviews tasks, the model can be trained.")

        # iterate over pending or all
        for idx, row in comp_tasks.iterrows():
            with st.expander(f"Task: {row['TaskTitle']} — by {row['Employee']} (Status: {row['Status']})"):
                st.markdown(f"**Description:** {row['Description']}")
                st.markdown(f"**Employee reported:** {row['EmployeeCompletion']}%")

                # model suggestion
                suggestion = row["EmployeeCompletion"]
                if model is not None and not np.isnan(row["EmployeeCompletion"]):
                    try:
                        suggestion = float(model.predict(np.array([[row["EmployeeCompletion"]]]))[0])
                    except Exception:
                        suggestion = row["EmployeeCompletion"]

                    st.info(f"🤖 AI Suggestion (boss likely): {suggestion:.2f}%")

                # boss adjustment slider defaults to suggestion (rounded)
                default_adj = int(round(suggestion))
                adjusted = st.slider(f"Set Boss Adjusted Completion (%) for this task", 0, 100, default_adj, key=f"adj_{row['TaskID']}")
                marks = marks_from_percentage(adjusted, task_total=5.0)
                comments = st.text_area("Boss Comments", value=row.get("BossComments", ""), key=f"comm_{row['TaskID']}")

                col1, col2, col3 = st.columns(3)
                col1.write(f"Adjusted Completion: **{adjusted}%**")
                col2.write(f"Marks (task): **{marks} / 5**")
                col3.write(f"Current Status: **{row['Status']}**")

                if st.button("Save Review", key=f"save_{row['TaskID']}"):
                    # update the dataframe
                    df = st.session_state.tasks_df
                    loc = df.index[df["TaskID"] == row["TaskID"]].tolist()
                    if loc:
                        i = loc[0]
                        st.session_state.tasks_df.at[i, "BossAdjusted"] = adjusted
                        st.session_state.tasks_df.at[i, "Marks"] = marks
                        st.session_state.tasks_df.at[i, "Status"] = "Reviewed"
                        st.session_state.tasks_df.at[i, "BossComments"] = comments
                        st.success("Review saved. This row will be used for ML training when you retrain the model.")
                        # reload local variables to reflect change
                        comp_tasks = st.session_state.tasks_df[st.session_state.tasks_df["Company"] == company].reset_index(drop=True)
                    else:
                        st.error("Failed to locate the task to update.")

        st.markdown("---")
        # Option to retrain immediately using current reviewed data
        if st.button("Retrain Linear Regression from Reviewed Data"):
            new_model, metrics = train_linear_model(st.session_state.tasks_df)
            if new_model is None:
                st.warning("Not enough reviewed data to train (need at least 3 reviewed entries).")
            else:
                model = new_model
                st.success(f"Model retrained. RMSE: {metrics['rmse']:.3f}, R²: {metrics['r2']:.3f} (trained on {metrics['trained_on']} rows).")

        # Show company table and export
        st.subheader("Company Task Records (latest)")
        st.dataframe(st.session_state.tasks_df[st.session_state.tasks_df["Company"] == company].sort_values("Timestamp", ascending=False))
        csv = st.session_state.tasks_df[st.session_state.tasks_df["Company"] == company].to_csv(index=False).encode("utf-8")
        st.download_button("Download Company CSV", csv, file_name=f"{company}_tasks.csv", mime="text/csv")

# ---------------------------
# Client view (view-only per company)
# ---------------------------
elif role == "Client":
    st.header(f"Client View — {company} — {user}")
    comp_df = st.session_state.tasks_df[st.session_state.tasks_df["Company"] == company]
    if comp_df.empty:
        st.info("No tasks for your company yet.")
    else:
        st.subheader("Company Tasks")
        st.dataframe(comp_df.sort_values("Timestamp", ascending=False))

        # Simple search in task titles/descriptions
        st.subheader("Search Tasks (keyword-based)")
        q = st.text_input("Enter search keywords")
        if q:
            mask = comp_df["TaskTitle"].str.contains(q, case=False, na=False) | comp_df["Description"].str.contains(q, case=False, na=False)
            res = comp_df[mask]
            st.write(f"Found {len(res)} matches")
            st.dataframe(res)

        # Sentiment summary of boss comments
        if "BossComments" in comp_df.columns:
            comments = comp_df["BossComments"].dropna().astype(str)
            if len(comments) > 0:
                sentiments = comments.apply(simple_sentiment)
                summary = sentiments.value_counts().to_dict()
                st.subheader("Boss Comments Sentiment (keyword-based)")
                st.write(summary)
            else:
                st.info("No boss comments yet to analyze.")

