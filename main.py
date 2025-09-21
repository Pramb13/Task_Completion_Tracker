import streamlit as st
from pinecone import Pinecone, ServerlessSpec
import numpy as np
import uuid
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC

# ----------------------------
# Initialize Pinecone client
# ----------------------------
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])  # API key stored in Streamlit secrets

index_name = "task-tracker"
dimension = 128  # must match vector length you upsert

# Create index if not exists
if index_name not in [idx["name"] for idx in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Connect to index
index = pc.Index(index_name)

# ----------------------------
# ML Models
# ----------------------------
# Linear Regression: predict marks
lin_reg = LinearRegression()
lin_reg.fit([[0], [100]], [0, 5])

# Logistic Regression: predict status
log_reg = LogisticRegression()
log_reg.fit([[0], [50], [100]], [0, 0, 1])  # <60 delayed, else on track

# SVM: sentiment on comments
vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(["good work", "excellent", "needs improvement", "bad performance"])
y_train = [1, 1, 0, 0]  # 1=Positive, 0=Negative
svm_clf = SVC()
svm_clf.fit(X_train, y_train)

# ----------------------------
# Helpers
# ----------------------------
def random_vector(dim=dimension):
    return np.random.rand(dim).tolist()

def safe_metadata(md: dict):
    """Ensure metadata values are JSON serializable"""
    clean = {}
    for k, v in md.items():
        if isinstance(v, (np.generic,)):
            v = v.item()
        clean[k] = v
    return clean

# ----------------------------
# App
# ----------------------------
st.title("📊 AI-Powered Task Completion & Review System")

role = st.sidebar.selectbox("Login as", ["Team Member", "Manager", "Client"])

# ----------------------------
# Team Member Role
# ----------------------------
if role == "Team Member":
    st.header("👩‍💻 Team Member Section")

    company = st.text_input("🏢 Enter Company Name")
    employee = st.text_input("👤 Enter Your Name")
    task = st.text_input("📝 Enter Task Title")
    completion = st.slider("✅ Completion %", 0, 100, 0)

    if st.button("📩 Submit Task"):
        if company and employee and task:
            marks = lin_reg.predict([[completion]])[0]
            status = log_reg.predict([[completion]])[0]
            status_text = "On Track" if status == 1 else "Delayed"

            task_id = str(uuid.uuid4())
            index.upsert(
                vectors=[{
                    "id": task_id,
                    "values": random_vector(),
                    "metadata": safe_metadata({
                        "company": company,
                        "employee": employee,
                        "task": task,
                        "completion": float(completion),
                        "marks": float(marks),
                        "status": status_text,
                        "reviewed": False
                    })
                }]
            )
            st.success(f"✅ Task '{task}' submitted by {employee} for {company}")
        else:
            st.error("❌ Please fill all fields before submitting.")

# ----------------------------
# Client Role
# ----------------------------
elif role == "Client":
    st.header("👨‍💼 Client Section")
    company = st.text_input("🏢 Enter Company Name")

    if st.button("🔍 View Approved Tasks"):
        if company:
            res = index.query(
                vector=random_vector(),
                top_k=100,
                include_metadata=True,
                filter={"company": {"$eq": company}, "reviewed": {"$eq": True}}
            )

            if res.matches:
                st.subheader(f"📌 Approved Tasks for {company}")
                for match in res.matches:
                    md = match.metadata or {}
                    employee = md.get("employee", "Unknown")
                    task = md.get("task", "Untitled")
                    completion = md.get("completion", 0.0)
                    marks = md.get("marks", 0.0)
                    status = md.get("status", "Not Reviewed")
                    sentiment = md.get("sentiment", "N/A")

                    st.write(
                        f"👤 {employee} | **{task}** → {completion}% "
                        f"(AI Marks: {marks:.2f}) | Status: {status}"
                    )
                    st.write(f"📝 Manager Comment Sentiment: {sentiment}")
            else:
                st.warning("⚠️ No approved tasks found for this company.")
        else:
            st.error("❌ Please enter a company name.")

# ----------------------------
# Manager Role
# ----------------------------
elif role == "Manager":
    st.header("👨‍💼 Manager Review Section")
    company = st.text_input("🏢 Enter Company Name")

    if st.button("📂 Load Tasks for Review"):
        if company:
            res = index.query(
                vector=random_vector(),
                top_k=100,
                include_metadata=True,
                include_values=True,
                filter={"company": {"$eq": company}, "reviewed": {"$eq": False}}
            )

            if res.matches:
                total_marks, possible_marks = 0, 0
                st.subheader(f"📌 Pending Review Tasks for {company}")

                for match in res.matches:
                    md = match.metadata or {}
                    emp = md.get("employee", "Unknown")
                    task = md.get("task", "Untitled")
                    emp_completion = float(md.get("completion", 0))

                    st.write(f"👤 {emp} | Task: **{task}**")
                    st.write(f"Reported Completion: {emp_completion}%")

                    # Manager adjusts completion %
                    manager_completion = st.slider(
                        f"✅ Manager Adjusted Completion for {emp} - {task}",
                        0, 100, int(emp_completion),
                        key=match.id
                    )

                    # AI predictions
                    predicted_marks = float(lin_reg.predict([[manager_completion]])[0])
                    status = log_reg.predict([[manager_completion]])[0]
                    status_text = "On Track" if status == 1 else "Delayed"

                    st.write(f"🤖 AI Predicted Marks: {predicted_marks:.2f}/5")
                    st.write(f"📌 AI Status: {status_text}")

                    # Manager comments + Sentiment
                    comments = st.text_area(
                        f"📝 Manager Comments for {emp} - {task}",
                        key=f"c_{match.id}"
                    )
                    sentiment_text = "N/A"
                    if comments:
                        try:
                            X_new = vectorizer.transform([comments])
                            sentiment = svm_clf.predict(X_new)[0]
                            sentiment_text = "Positive" if sentiment == 1 else "Negative"
                            st.write(f"🤖 AI Detected Sentiment: {sentiment_text}")
                        except Exception:
                            sentiment_text = "N/A"

                    # --- Update Pinecone safely ---
                    safe_values = match.values if hasattr(match, "values") and match.values else random_vector()
                    safe_meta = safe_metadata({
                        **md,
                        "completion": float(manager_completion),
                        "marks": predicted_marks,
                        "status": status_text,
                        "reviewed": True,
                        "comments": comments,
                        "sentiment": sentiment_text
                    })

                    try:
                        index.upsert(vectors=[{
                            "id": match.id,
                            "values": safe_values,
                            "metadata": safe_meta
                        }])
                    except Exception as e:
                        st.error(f"❌ Update failed for task {task}: {e}")

                    total_marks += predicted_marks
                    possible_marks += 5

                st.subheader(f"📊 Total AI-Predicted Marks: {total_marks:.2f} / {possible_marks}")
                st.success("✅ Review completed. All tasks updated.")
            else:
                st.warning("⚠️ No pending tasks found for this company.")
        else:
            st.error("❌ Please enter a company name.")
