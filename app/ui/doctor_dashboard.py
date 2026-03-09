import streamlit as st

from app.services.record_service import create_record, view_record
from app.models.record_model import get_doctor_all_patients, get_patient_records
from app.ui.referral_ui import referral_ui
from app.ui.emergency_ui import emergency_ui
from app.ui.access_logs_ui import access_logs_ui


def doctor_dashboard(user):
    # ==================================================
    # SIDEBAR (NAVIGATION)
    # ==================================================
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        st.markdown("**Go to:**")
        st.button("🏠 Home", use_container_width=True)
        st.button("👥 My Patients", use_container_width=True)
        st.button("📌 Pinned Patients", use_container_width=True)
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ==================================================
    # HEADER
    # ==================================================
    st.markdown(
        f"""
        <div class="gradient-header">
            <h1>👨‍⚕️ Doctor Dashboard</h1>
            <p>
                Welcome, Dr. {user['username']}
                <span class="role-badge">DOCTOR</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==================================================
    # METRICS
    # ==================================================
    patients = get_doctor_all_patients(user["id"])
    patient_count = len(patients)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="card metric">
                <h2>{patient_count}</h2>
                <p>My Patients</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card metric">
                <h2>1</h2>
                <p>Pinned</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card metric">
                <h2>0</h2>
                <p>Total Records</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            """
            <div class="card metric">
                <h2>4</h2>
                <p>Recent Activity</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ==================================================
    # MAIN CONTENT
    # ==================================================
    left, right = st.columns(2)

    # -------------------------------
    # QUICK ACTIONS
    # -------------------------------
    with left:
        st.markdown("### ⚡ Quick Actions")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        patient_id = st.number_input("Patient ID", min_value=1, step=1)
        record_text = st.text_area("New Medical Record")

        if st.button("➕ Add Medical Record", type="primary", use_container_width=True):
            if record_text.strip():
                create_record(
                    plain_text=record_text,
                    patient_id=int(patient_id),
                    doctor_user=user
                )
                st.success("Medical record added")
            else:
                st.warning("Record cannot be empty")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # TODAY'S PATIENTS
    # -------------------------------
    with right:
        st.markdown("### 📋 Today's Patients")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if patients:
            for p in patients[:3]:
                st.markdown(
                    f"""
                    **👤 {p['username']}**  
                    Records: {len(get_patient_records(p['id']))}
                    """
                )
                st.button("View", key=f"view_{p['id']}")
                st.divider()
        else:
            st.info("No patients found")

        st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # PATIENT MANAGEMENT (DETAILED)
    # ==================================================
    st.markdown("### 🧠 Patient Management")

    if patients:
        patient_map = {p["username"]: p["id"] for p in patients}
        selected_patient = st.selectbox(
            "Select Patient",
            patient_map.keys(),
            index=None,
            placeholder="Choose a patient"
        )

        if selected_patient:
            pid = patient_map[selected_patient]
            records = get_patient_records(pid)

            st.markdown('<div class="card">', unsafe_allow_html=True)

            if records:
                for r in records:
                    if st.button(f"View Record #{r['id']}", key=f"rec_{r['id']}"):
                        text = view_record(
                            record_id=r["id"],
                            user_id=user["id"],
                            user_private_key=user["rsa_private_key"]
                        )
                        st.text_area(
                            "Medical Record",
                            text,
                            height=200
                        )
            else:
                st.info("No records found")

            referral_ui(user)
            emergency_ui(user)

            st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # ACCESS LOGS
    # ==================================================
    access_logs_ui(user)
