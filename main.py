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
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])  # API key in Streamlit secrets

index_name = "task-tracker"
dimension = 128  # for demo purpose

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
# Dummy ML Models
# ----------------------------
# Linear Regression for marks prediction
lin_reg = LinearRegression()
lin_reg.fit([[0], [100]], [0, 5])  # 0% -> 0 marks, 100% -> 5 marks

# Logistic Regression for status (on track / delayed)
log_reg = LogisticRegression()
log_reg.fit([[0], [50], [100]], [0, 0, 1])  # Below 60 = delayed, else on track

# SVM for sentiment (positive / negative)
vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(["good work", "excellent", "needs improvement", "bad performance"])
y_train = [1, 1, 0, 0]  # 1=Positive, 0=Negative
svm_clf = SVC()
svm_clf.fit(X_train, y_train)

# ----------------------------
# Helper function
# ----------------------------
def random_vector(dim=dimension):
    return np.random.rand(dim).tolist()

# ----------------------------
# Streamlit App
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
                    "metadata": {
                        "company": company,
                        "employee": employee,
                        "task": task,
                        "completion": completion,
                        "marks": float(marks),
                        "status": status_text,
                        "reviewed": False
                    }
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
                    md = match.metadata
                    st.write(
                        f"👤 {md['employee']} | **{md['task']}** → {md['completion']}% "
                        f"(AI Marks: {md['marks']:.2f}) | Status: {md['status']}"
                    )
                    st.write(f"📝 Manager Comment Sentiment: {md.get('sentiment', 'N/A')}")
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
                    md = match.metadata
                    emp_completion = md.get("completion", 0)

                    st.write(f"👤 {md.get('employee')} | Task: **{md.get('task')}**")
                    st.write(f"Reported Completion: {emp_completion}%")

                    # Manager adjusts completion
                    manager_completion = st.slider(
                        f"✅ Manager Adjusted Completion for {md.get('employee')} - {md.get('task')}",
                        0, 100, int(emp_completion), key=match.id
                    )

                    # AI predictions on adjusted value
                    predicted_marks = lin_reg.predict([[manager_completion]])[0]
                    status = log_reg.predict([[manager_completion]])[0]
                    status_text = "On Track" if status == 1 else "Delayed"

                    st.write(f"🤖 AI Predicted Marks: {predicted_marks:.2f}/5")
                    st.write(f"📌 AI Status: {status_text}")

                    # Manager comments + Sentiment
                    comments = st.text_area(f"📝 Manager Comments for {md.get('employee')} - {md.get('task')}", key=f"c_{match.id}")
                    sentiment_text = "N/A"
                    if comments:
                        X_new = vectorizer.transform([comments])
                        sentiment = svm_clf.predict(X_new)[0]
                        sentiment_text = "Positive" if sentiment == 1 else "Negative"
                        st.write(f"🤖 AI Detected Sentiment: {sentiment_text}")

                    # Update in Pinecone
                    values = match.values if hasattr(match, "values") and match.values else random_vector()

                    index.upsert(
                        vectors=[{
                            "id": match.id,
                            "values": values,
                            "metadata": {
                                **md,
                                "completion": manager_completion,
                                "marks": float(predicted_marks),
                                "status": status_text,
                                "reviewed": True,
                                "comments": comments,
                                "sentiment": sentiment_text
                            }
                        }]
                    )

                    total_marks += predicted_marks
                    possible_marks += 5

                st.subheader(f"📊 Total AI-Predicted Marks: {total_marks:.2f} / {possible_marks}")
                st.success("✅ Review completed. All tasks updated.")
            else:
                st.warning("⚠️ No pending tasks found for this company.")
        else:
            st.error("❌ Please enter a company name.")
