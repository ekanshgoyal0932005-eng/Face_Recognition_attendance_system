
import streamlit as st
import subprocess
import sys
import os
import json
import hashlib
import pandas as pd
import plotly.express as px
from datetime import datetime
from face_register import register_face
from auth import login_page

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

st.set_page_config(
    page_title="Face Attendance System",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_page()
    st.stop()

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f8f5ff, #f1f7ff, #f5fbf8);
}

header {
    background: transparent !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #eee8fa, #e8f1fc);
    border-right: 1px solid #e3dced;
}

[data-testid="stSidebar"] * {
    color: #45415b;
}

h1, h2, h3 {
    color: #39364f !important;
    font-weight: 800 !important;
}

p, label {
    color: #6f6b82;
}

.hero {
    background: linear-gradient(120deg, #e6ddf7, #dceafa, #e0f3e9);
    padding: 32px;
    border-radius: 24px;
    margin-bottom: 28px;
    animation: fadeUp 0.8s ease;
    box-shadow: 0 8px 25px rgba(100, 90, 140, 0.08);
}

.hero h1 {
    font-size: 32px;
    margin-bottom: 8px;
}

.hero p {
    font-size: 15px;
    margin-bottom: 0;
}

.stat-card {
    padding: 24px;
    border-radius: 20px;
    min-height: 145px;
    box-shadow: 0 5px 20px rgba(80, 75, 110, 0.06);
    transition: all 0.3s ease;
    animation: fadeUp 0.7s ease;
}

.stat-card:hover {
    transform: translateY(-7px);
    box-shadow: 0 12px 28px rgba(80, 75, 110, 0.13);
}

.stat-card h4 {
    color: #625d78;
    font-size: 14px;
    font-weight: 600;
}

.stat-card h2 {
    font-size: 34px;
    margin: 10px 0;
}

.stat-card span {
    font-size: 27px;
}

.lavender { background: #e9e0f8; }
.blue { background: #deebfa; }
.mint { background: #ddf1e7; }
.peach { background: #f9e8dd; }

.section-card {
    background: rgba(255,255,255,0.75);
    border: 1px solid #ebe6f1;
    padding: 24px;
    border-radius: 20px;
    margin-bottom: 20px;
    animation: fadeUp 0.7s ease;
}

div.stButton > button {
    background: linear-gradient(110deg, #b9a8df, #a9c5e8);
    color: #302d43;
    border: none;
    border-radius: 12px;
    padding: 11px 22px;
    font-weight: 700;
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 7px 18px rgba(140, 125, 190, 0.25);
    color: #302d43;
    border: none;
}

.stTextInput input {
    border-radius: 12px;
    background: #ffffff;
}

[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #eee8f5;
}

[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

.float-icon {
    display: inline-block;
    animation: float 3s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)


# ---------------- DATA FUNCTIONS ----------------

def load_students():
    path = os.path.join(BASE_DIR, "students.json")

    if os.path.exists(path):
        with open(path, "r") as file:
            return json.load(file)

    return {}


def load_attendance():
    path = os.path.join(BASE_DIR, "attendance", "attendance.csv")

    if os.path.exists(path):
        return pd.read_csv(path)

    return pd.DataFrame(columns=[
        "Student ID", "Name", "Date", "Time"
    ])


students = load_students()
attendance_df = load_attendance()

today = datetime.now().strftime("%Y-%m-%d")

if not attendance_df.empty and "Date" in attendance_df.columns:
    today_df = attendance_df[
        attendance_df["Date"].astype(str) == today
    ]
    present = today_df["Student ID"].nunique()
else:
    today_df = pd.DataFrame()
    present = 0

total_students = len(students)
attendance_rate = round(
    (present / total_students) * 100
) if total_students else 0


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown(
        '<div style="text-align:center;padding:20px 5px;">'
        '<div style="font-size:42px;" class="float-icon">📸</div>'
        '<h2 style="font-size:21px;">FaceAttend</h2>'
        '<p style="font-size:12px;">Smart Attendance System</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "MAIN MENU",
        [
            "🏠 Dashboard",
            "📊 Attendance Analytics",
            "👤 Register Student",
            "🧠 Train Model",
            "📷 Mark Attendance",
            "📋 Attendance Records"
        ],
        label_visibility="visible"
    )

    st.markdown("---")
    st.caption("AI Powered Attendance")
    st.caption("Version 3.0")

    st.markdown("---")

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>Facial Recognition Attendance</h1>
    <p>Your smart, seamless and automated attendance management workspace.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- DASHBOARD ----------------

if page == "🏠 Dashboard":

    st.subheader("Welcome Back! 👋")
    st.caption(datetime.now().strftime("%A, %d %B %Y"))

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (c1, "Registered Students", total_students, "👨‍🎓", "lavender"),
        (c2, "Present Today", present, "✅", "mint"),
        (c3, "Absent Today", max(total_students - present, 0), "📅", "peach"),
        (c4, "Attendance Rate", f"{attendance_rate}%", "📊", "blue")
    ]

    for col, title, value, emoji, color in cards:
        with col:
            st.markdown(f"""
            <div class="stat-card {color}">
                <span>{emoji}</span>
                <h4>{title}</h4>
                <h2>{value}</h2>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    left, right = st.columns([1.5, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Today's Attendance")

        if not today_df.empty:
            st.dataframe(
                today_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No attendance recorded today yet.")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Quick Overview")

        st.write("👨‍🎓 Total Students:", total_students)
        st.write("✅ Present Today:", present)
        st.write("📅 Date:", today)

        st.progress(min(attendance_rate, 100) / 100)
        st.caption(f"{attendance_rate}% attendance recorded today.")

        st.markdown('</div>', unsafe_allow_html=True)


# ---------------- ATTENDANCE ANALYTICS ----------------

elif page == "📊 Attendance Analytics":

    st.subheader("📊 Attendance Analytics")
    st.caption("Analyze daily, weekly, monthly and student-wise attendance.")

    if not attendance_df.empty:

        df = attendance_df.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        if not df.empty:

            daily = df.groupby(
                df["Date"].dt.date
            )["Student ID"].nunique().reset_index()

            daily.columns = ["Date", "Students Present"]

            fig = px.bar(
                daily,
                x="Date",
                y="Students Present",
                title="Daily Attendance",
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)

            df["Week"] = df["Date"].dt.to_period("W").astype(str)

            weekly = df.groupby(
                "Week"
            )["Student ID"].nunique().reset_index()

            weekly.columns = ["Week", "Students Present"]

            fig2 = px.line(
                weekly,
                x="Week",
                y="Students Present",
                markers=True,
                title="Weekly Attendance Trend",
                template="plotly_white"
            )

            st.plotly_chart(fig2, use_container_width=True)

            df["Month"] = df["Date"].dt.to_period("M").astype(str)

            monthly = df.groupby(
                "Month"
            )["Student ID"].nunique().reset_index()

            monthly.columns = ["Month", "Students Present"]

            fig3 = px.bar(
                monthly,
                x="Month",
                y="Students Present",
                title="Monthly Attendance",
                template="plotly_white"
            )

            st.plotly_chart(fig3, use_container_width=True)

            total_days = df["Date"].dt.date.nunique()
            total_registered = max(len(students), 1)

            student_stats = df.groupby(
                ["Student ID", "Name"]
            ).size().reset_index(name="Days Present")

            student_stats["Attendance Percentage"] = (
                student_stats["Days Present"] /
                max(total_days, 1) * 100
            ).round(2)

            fig4 = px.bar(
                student_stats,
                x="Name",
                y="Attendance Percentage",
                title="Student-wise Attendance Percentage",
                color="Attendance Percentage",
                template="plotly_white"
            )

            st.plotly_chart(fig4, use_container_width=True)

            st.subheader("Student Attendance Summary")

            st.dataframe(
                student_stats,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No valid attendance dates found.")

    else:
        st.info("No attendance data available yet. Mark some attendance first.")


# ---------------- REGISTER STUDENT ----------------

elif page == "👤 Register Student":

    st.subheader("Register New Student")
    st.caption("Add a student and capture their face data.")

    with st.container(border=True):

        student_id = st.text_input(
            "Student ID",
            placeholder="Enter numeric ID"
        )

        name = st.text_input(
            "Student Name",
            placeholder="Enter full name"
        )

        st.info("Make sure your camera is connected before capturing images.")

        if st.button("📸 Capture Face", use_container_width=True):

            if student_id.isdigit() and name.strip():

                if student_id in students:
                    st.error("This Student ID is already registered.")

                else:
                    with st.spinner("Opening camera and capturing face images..."):
                        result = register_face(student_id, name.strip())

                    if "successfully" in result.lower():
                        st.success(result)
                        st.balloons()
                    else:
                        st.error(result)

            else:
                st.error("Enter a valid numeric Student ID and name.")


# ---------------- TRAIN MODEL ----------------

elif page == "🧠 Train Model":

    st.subheader("Train Recognition Model")
    st.caption("Train the AI model using registered student face images.")

    st.markdown("""
    <div class="section-card">
        <h3>🧠 Model Training</h3>
        <p>Training helps the system recognize registered students using their face data.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Train Model", use_container_width=True):

        with st.spinner("Training your face recognition model..."):

            result = subprocess.run(
                [sys.executable, os.path.join(BASE_DIR, "train_model.py")],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )

        if result.returncode == 0:
            st.success("Model trained successfully!")
            st.balloons()

            if result.stdout:
                st.code(result.stdout)

        else:
            st.error("Model training failed.")

            if result.stderr:
                st.code(result.stderr)


# ---------------- MARK ATTENDANCE ----------------

elif page == "📷 Mark Attendance":

    st.subheader("Face Recognition Attendance")
    st.caption("Start the camera to recognize students and record attendance.")

    st.markdown("""
    <div class="section-card">
        <h3>📷 Camera Control Center</h3>
        <p>Position your face in front of the camera. The system will identify registered students and record their attendance.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶ Start Attendance Camera", use_container_width=True):

        model_path = os.path.join(BASE_DIR, "trainer", "face_model.yml")

        if os.path.exists(model_path):

            subprocess.Popen(
                [sys.executable, os.path.join(BASE_DIR, "mark_attendance.py")],
                cwd=BASE_DIR
            )

            st.success("Attendance camera launched successfully!")

        else:
            st.warning("Please train the model before starting attendance.")


# ---------------- ATTENDANCE RECORDS ----------------

elif page == "📋 Attendance Records":

    st.subheader("Attendance Records")
    st.caption("View and download student attendance history.")

    file_path = os.path.join(
        BASE_DIR, "attendance", "attendance.csv"
    )

    if os.path.exists(file_path):

        df = pd.read_csv(file_path)

        if not df.empty:

            search = st.text_input(
                "🔍 Search Student",
                placeholder="Search by name or student ID"
            )

            if search:
                df = df[
                    df["Name"].astype(str).str.contains(
                        search, case=False, na=False
                    )
                    | df["Student ID"].astype(str).str.contains(
                        search, case=False, na=False
                    )
                ]

            st.markdown("### Attendance History")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "⬇ Download Attendance CSV",
                df.to_csv(index=False),
                "attendance_report.csv",
                "text/csv",
                use_container_width=True
            )

        else:
            st.info("Attendance file is currently empty.")

    else:
        st.info("No attendance records found yet.")


# ---------------- FOOTER ----------------

st.markdown("""
<div style="text-align:center;padding:35px 0 10px 0;color:#9993aa;font-size:12px;">
    FaceAttend • Smart Attendance Management System
</div>
""", unsafe_allow_html=True)
