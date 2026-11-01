import streamlit as st
import json
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_FILE = os.path.join(BASE_DIR, "admin.json")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    if not os.path.exists(AUTH_FILE):
        default_admin = {
            "username": "admin",
            "password": hash_password("admin123")
        }
        with open(AUTH_FILE, "w") as file:
            json.dump(default_admin, file)

    with open(AUTH_FILE, "r") as file:
        admin = json.load(file)

    return (
        username == admin["username"]
        and hash_password(password) == admin["password"]
    )

def login_page():
    st.markdown("<h1 style='text-align:center;'>🔐 Admin Login</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Face Attendance System</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if check_login(username, password):
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid username or password!")