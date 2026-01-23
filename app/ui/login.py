import streamlit as st
from app.services.auth_service import authenticate_user


def login_page():
    st.title("🔐 Eyes of Asclepius")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = authenticate_user(username, password)
            st.session_state["user"] = user
            st.success("Login successful")
            st.rerun()
        except ValueError:
            st.error("Invalid username or password")
