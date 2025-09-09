import streamlit as st
from pinecone import Pinecone, ServerlessSpec
import uuid

# ----------------------------
# Pinecone Initialization
# ----------------------------
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "task"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=8,  # small since we only use metadata
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# ----------------------------
# Utility
# ----------------------------
def calculate_task_marks(completion_percentage, total_marks=5):
    return total_marks * (completion_percentage / 100)

# ----------------------------
# App Title
# ----------------------------
st.title("📊 Task Completion Tracker (with Pinecone)")

# ----------------------------
# Sidebar Role Selection
# ----------------------------
role = st.sidebar.selectbox("Select Role", ["Employee", "Client", "Boss"])

# ----------------------------
# EMPLOYEE
# ----------------------------
if role == "Employee":
    st.header("👩‍💻 Employee Section")

    company_name = st.text_input("Enter Company Name")
    employee_name = st.text_input("Enter Your Name")
    task_name = st.text_input("Enter Task Name")
    completion = st.slider("Task Completion %", 0, 100, 0, 5)

    if st.button("Submit Task"):
        if company_name and employee_name and task_name:
            marks = calculate_task_marks(completion)
            task_id = str(uuid.uuid4())

            index.upsert([
                {
                    "id": task_id,
                    "values": [0.0] * 8,  # placeholder vector
                    "metadata": {
                        "company": company_name,
                        "employee": employee_name,
                        "task": task_name,
                        "completion": completion,
                        "boss_adjustment": completion,
                        "marks": marks
                    }
                }
            ])
            st.success(f"✅ Task '{task_name}' submitted for {company_name} by {employee_name}")
        else:
            st.error("Please fill all fields before submitting!")

# ----------------------------
# CLIENT
# ----------------------------
elif role == "Client":
    st.header("👨‍💼 Client Section")

    company_name = st.text_input("Enter Company Name")

    if company_name:
        results = index.query(
            vector=[0.0] * 8,
            filter={"company": {"$eq": company_name}},
            top_k=100,
            include_metadata=True
        )

        if results.matches:
            st.subheader(f"📌 Tasks for {company_name}")
            for match in results.matches:
                md = match.metadata
                st.write(f"- 👤 {md['employee']} → {md['task']} : {md['completion']}% (Marks: {md['marks']:.2f})")
        else:
            st.warning("No tasks found for this company!")

# ----------------------------
# BOSS
# ----------------------------
elif role == "Boss":
    st.header("👨‍💼 Boss Review Section")

    company_name = st.text_input("Enter Company Name")

    if company_name:
        results = index.query(
            vector=[0.0] * 8,
            filter={"company": {"$eq": company_name}},
            top_k=100,
            include_metadata=True
        )

        if results.matches:
            total_marks_obtained = 0
            total_marks_possible = 0

            for match in results.matches:
                md = match.metadata

                st.write(f"### 👤 {md['employee']} - {md['task']}")
                st.write(f"Employee entered: {md['completion']}%")

                boss_adjust = st.slider(
                    f"Boss adjust % for {md['employee']} - {md['task']}",
                    0, 100, int(md['boss_adjustment']), 5,
                    key=match.id
                )

                new_marks = calculate_task_marks(boss_adjust)

                # Update in Pinecone
                index.update(
                    id=match.id,
                    set_metadata={
                        "boss_adjustment": boss_adjust,
                        "marks": new_marks
                    }
                )

                st.write(f"✅ Adjusted Marks: {new_marks:.2f}/5")

                total_marks_obtained += new_marks
                total_marks_possible += 5

            st.subheader(f"📌 Total Marks for {company_name}: {total_marks_obtained:.2f}/{total_marks_possible}")

            approved = st.radio("Is the work approved?", ("Yes", "No"))
            comments = st.text_area("Boss's Comments", "Enter your feedback here...")

            if st.button("Submit Review"):
                st.success("Review Submitted ✅")
                st.write(f"**Approval:** {approved}")
                st.write(f"**Comments:** {comments}")
        else:
            st.warning("No tasks found for this company!")
