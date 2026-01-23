import streamlit as st

from app.ui.login import login_page
from app.ui.doctor_dashboard import doctor_dashboard
from app.ui.patient_dashboard import patient_dashboard
from app.ui.admin_dashboard import admin_dashboard
from app.ui.style import inject_global_css


def main():
    # ----------------------------------
    # Global page config
    # ----------------------------------
    st.set_page_config(
        page_title="Eyes of Asclepius",
        page_icon="🧿",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # ----------------------------------
    # Global styling
    # ----------------------------------
    inject_global_css()

    # ----------------------------------
    # Authentication gate
    # ----------------------------------
    if "user" not in st.session_state:
        login_page()
        return

    user = st.session_state["user"]

    # ----------------------------------
    # Role-based routing
    # ----------------------------------
    if user["role"] == "doctor":
        doctor_dashboard(user)

    elif user["role"] == "patient":
        patient_dashboard(user)

    elif user["role"] == "admin":
        admin_dashboard(user)

    else:
        st.error("Unauthorized role detected")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    main()
