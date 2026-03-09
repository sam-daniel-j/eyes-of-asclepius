import streamlit as st
from app.services.auth_service import authenticate_user


def login_page():

    left, center, right = st.columns([1, 2, 1])

    with center:

        st.markdown(
            """
            <div class="gradient-header" style="text-align:center;">
                <h1>🧿 Eyes of Asclepius</h1>
                <p>Secure Medical Record Management System</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("### 🔐 System Login")

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        if st.button("Login", type="primary", use_container_width=True):
            if not username or not password:
                st.warning("Please enter both username and password")
            else:
                try:
                    user = authenticate_user(username, password)
                    st.session_state["user"] = user
                    st.success("Login successful")
                    st.rerun()
                except Exception:
                    st.error("Invalid username or password")


        st.markdown('</div>', unsafe_allow_html=True)


        st.markdown(
            """
            <div style="text-align:center; margin-top:1rem; color:#9ca3af;">
                © Eyes of Asclepius
            </div>
            """,
            unsafe_allow_html=True
        )
