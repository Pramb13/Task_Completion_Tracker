import streamlit as st
from pinecone import Pinecone, ServerlessSpec
import numpy as np
import uuid

# ----------------------------
# Initialize Pinecone client
# ----------------------------
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])  # keep API key in Streamlit secrets

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
    """Convert completion % into marks (out of 5)."""
    return total * (completion / 100)

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
            vector = np.random.rand(dimension).tolist()  # Dummy vector for demo

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
                            "boss_adjustment": completion,
                            "marks": marks,
                            "reviewed": False  # initially not reviewed
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
                        f"👤 {md['employee']} | **{md['task']}** → {md['boss_adjustment']}% "
                        f"(Marks: {md['marks']:.2f})"
                    )
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
                include_values=True,   # FIX: include values so we can re-upsert
                filter={"company": {"$eq": company}}
            )

            if res.matches:
                total_marks, possible_marks = 0, 0
                st.subheader(f"📌 Review Tasks for {company}")

                for match in res.matches:
                    md = match.metadata
                    st.write(f"👤 {md['employee']} | Task: **{md['task']}**")
                    st.write(f"Employee Completion: {md['completion']}%")

                    new_completion = st.slider(
                        f"Boss adjust for {md['employee']} - {md['task']}",
                        0, 100, int(md["boss_adjustment"]),
                        key=match.id
                    )

                    new_marks = calculate_task_marks(new_completion)

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
                                    "boss_adjustment": new_completion,
                                    "marks": new_marks,
                                    "reviewed": True   # mark as reviewed
                                }
                            }
                        ]
                    )

                    st.write(f"✅ Adjusted Marks: {new_marks:.2f}/5")
                    total_marks += new_marks
                    possible_marks += 5

                st.subheader(f"📊 Total: {total_marks:.2f} / {possible_marks}")

                approved = st.radio("Final Approval:", ["Yes", "No"])
                comments = st.text_area("📝 Boss's Comments")

                if st.button("✅ Submit Review"):
                    st.success("Review submitted successfully!")
                    st.write(f"**Approval:** {approved}")
                    st.write(f"**Comments:** {comments}")
            else:
                st.warning("⚠️ No tasks found for this company.")
        else:
            st.error("❌ Please enter a company name.")
