import streamlit as st
from pinecone import Pinecone, ServerlessSpec
import numpy as np
import uuid

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer

# ----------------------------
# Initialize Pinecone client
# ----------------------------
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])  # keep API key safe

index_name = "task-index"
dimension = 64  # demo dimension (use 384, 768, or 1536 if embeddings are used)

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
# Helper function
# ----------------------------
def calculate_task_marks(completion, total=5):
    return total * (completion / 100)

# ----------------------------
# Train ML models (Regression + Classification)
# ----------------------------
X_train = np.array([[0], [25], [50], [75], [100]])
y_marks = np.array([0, 1.25, 2.5, 3.75, 5])  # regression target
y_status = np.array([0, 0, 1, 1, 1])  # 0 = Delayed, 1 = On Track

lin_reg = LinearRegression().fit(X_train, y_marks)
log_reg = LogisticRegression().fit(X_train, y_status)

# Sentiment Analysis Model (SVM)
train_comments = ["Good job", "Excellent work", "Needs improvement", "Very poor progress"]
labels = [1, 1, 0, 0]  # 1=Positive, 0=Negative
vectorizer = TfidfVectorizer()
X_sent = vectorizer.fit_transform(train_comments)
svm_clf = SVC(kernel="linear")
svm_clf.fit(X_sent, labels)

# ----------------------------
# Streamlit App
# ----------------------------
st.title("📊 EvalTrack: AI-Powered Task Completion & Review")

role = st.sidebar.selectbox("Login as", ["Employee", "Client", "Boss"])

# ----------------------------
# Employee Role
# ----------------------------
if role == "Employee":
    st.header("👩‍💻 Employee Section")

    company = st.text_input("🏢 Enter Company Name")
    employee = st.text_input("👤 Enter Your Name")
    task = st.text_input("📝 Enter Task Title")
    completion = st.slider("✅ Completion %", 0, 100, 0)

    if st.button("📩 Submit Task"):
        if company and employee and task:
            marks = calculate_task_marks(completion)
            vector = np.random.rand(dimension).tolist()  # dummy vector

            task_id = str(uuid.uuid4())
            index.upsert(
                vectors=[
                    {
                        "id": task_id,
                        "values": vector,
                        "metadata": {
                            "company": company,
                            "employee": employee,
                            "task": task,
                            "completion": completion,
                            "marks": marks,
                            "reviewed": False,
                            "status": "Pending"
                        }
                    }
                ]
            )
            st.success(f"✅ Task '{task}' submitted for {company} by {employee}")
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
                vector=np.random.rand(dimension).tolist(),
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
                    st.write(f"📝 Boss Comment Sentiment: {md.get('sentiment', 'N/A')}")
            else:
                st.warning("⚠️ No approved tasks found for this company.")
        else:
            st.error("❌ Please enter a company name.")

# ----------------------------
# Boss Role
# ----------------------------
elif role == "Boss":
    st.header("👨‍💼 Boss Review Section")
    company = st.text_input("🏢 Enter Company Name")

    if st.button("📂 Load Tasks"):
        if company:
            res = index.query(
                vector=np.random.rand(dimension).tolist(),
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
                    completion = md["completion"]

                    # AI predictions
                    predicted_marks = lin_reg.predict([[completion]])[0]
                    status = log_reg.predict([[completion]])[0]
                    status_text = "On Track" if status == 1 else "Delayed"

                    st.write(f"👤 {md['employee']} | Task: **{md['task']}**")
                    st.write(f"Employee Reported Completion: {completion}%")
                    st.write(f"🤖 AI Predicted Marks: {predicted_marks:.2f}/5")
                    st.write(f"📌 AI Status: {status_text}")

                    # Boss feedback
                    comments = st.text_area(f"📝 Boss Comments for {md['employee']} - {md['task']}", key=match.id)
                    sentiment_text = "N/A"
                    if comments:
                        X_new = vectorizer.transform([comments])
                        sentiment = svm_clf.predict(X_new)[0]
                        sentiment_text = "Positive" if sentiment == 1 else "Negative"
                        st.write(f"🤖 AI Detected Sentiment: {sentiment_text}")

                    # Ensure vector exists
                    values = match.values if hasattr(match, "values") and match.values else np.random.rand(dimension).tolist()

                    # Update in Pinecone
                    index.upsert(
                        vectors=[
                            {
                                "id": match.id,
                                "values": values,
                                "metadata": {
                                    **md,
                                    "marks": float(predicted_marks),
                                    "status": status_text,
                                    "reviewed": True,
                                    "comments": comments,
                                    "sentiment": sentiment_text
                                }
                            }
                        ]
                    )

                    total_marks += predicted_marks
                    possible_marks += 5

                st.subheader(f"📊 Total AI-Predicted Marks: {total_marks:.2f} / {possible_marks}")

                if st.button("✅ Finalize Review"):
                    st.success("Review submitted and tasks marked as reviewed ✅")
            else:
                st.warning("⚠️ No pending tasks found for this company.")
        else:
            st.error("❌ Please enter a company name.")
