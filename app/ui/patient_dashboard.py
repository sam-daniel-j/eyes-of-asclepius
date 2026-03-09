import streamlit as st

from app.models.record_model import (
    get_patient_records,
    get_latest_record,
    get_patient_doctors,
    get_referral_doctors,
)
from app.services.record_service import view_record


def patient_dashboard(user):
    # ==================================================
    # SIDEBAR
    # ==================================================
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        st.markdown("**Go to:**")
        st.button("🏠 My Records", use_container_width=True)
        st.button("🩺 Health Summary", use_container_width=True)
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
            <h1>🧑 Patient Portal</h1>
            <p>
                Welcome, {user['username']}
                <span class="role-badge">PATIENT</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==================================================
    # CURRENT MEDICAL RECORD
    # ==================================================
    st.markdown("### 📌 My Medical Records")

    latest = get_latest_record(user["id"])

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if latest:
        try:
            record_text = view_record(
                record_id=latest["id"],
                user_id=user["id"],
                user_private_key=user["rsa_private_key"]
            )
            st.text_area(
                "Latest Medical Record",
                record_text,
                height=220
            )
        except Exception:
            st.warning("Unable to decrypt your medical record")
    else:
        st.info("📄 No medical records found. Visit your doctor for a checkup!")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # MEDICAL HISTORY
    # ==================================================
    records = get_patient_records(user["id"])

    if records:
        st.markdown("### 📜 Medical History")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        record_ids = [r["id"] for r in records]

        selected_record = st.selectbox(
            "Select a past record",
            record_ids,
            index=None,
            placeholder="Choose a record"
        )

        if selected_record:
            try:
                text = view_record(
                    record_id=int(selected_record),
                    user_id=user["id"],
                    user_private_key=user["rsa_private_key"]
                )
                st.text_area(
                    "Medical Record",
                    text,
                    height=220
                )
            except Exception:
                st.error("Access denied or record expired")

        st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # DOCTORS INFO
    # ==================================================
    col1, col2 = st.columns(2)

    # -------------------------------
    # PRIMARY DOCTORS
    # -------------------------------
    with col1:
        st.markdown("### 👨‍⚕️ Primary Doctor(s)")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        doctors = get_patient_doctors(user["id"])
        if doctors:
            for d in doctors:
                st.markdown(
                    f"- **{d['username']}** "
                    f"({d['specialization'] or 'General'})"
                )
        else:
            st.info("No primary doctors assigned")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # REFERRAL DOCTORS
    # -------------------------------
    with col2:
        st.markdown("### 🔁 Referral Doctor(s)")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        referrals = get_referral_doctors(user["id"])
        if referrals:
            for r in referrals:
                st.markdown(
                    f"- **{r['username']}** "
                    f"({r['specialization'] or 'General'})"
                )
        else:
            st.info("No referral doctors")

        st.markdown('</div>', unsafe_allow_html=True)
