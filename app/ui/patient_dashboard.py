import streamlit as st

from app.models.record_model import (
    get_patient_records,
    get_latest_record,
    get_patient_doctors,
    get_referral_doctors,
)
from app.services.record_service import view_record


def patient_dashboard(user):
    st.title(f"🧍 Patient Dashboard — {user['username']}")

    # ==================================================
    # CURRENT (LATEST) MEDICAL RECORD
    # ==================================================
    st.subheader("📌 Current Medical Record")

    latest = get_latest_record(user["id"])

    if latest:
        try:
            latest_text = view_record(
                record_id=latest["id"],
                user_id=user["id"],
                user_private_key=user["rsa_private_key"]
            )
            st.text_area(
                "Latest Medical Record",
                latest_text,
                height=220
            )
        except Exception:
            st.warning("Unable to decrypt the latest medical record")
    else:
        st.info("No medical records available yet")

    st.divider()

    # ==================================================
    # MEDICAL HISTORY
    # ==================================================
    st.subheader("📜 Medical History")

    records = get_patient_records(user["id"])

    if records:
        record_ids = [r["id"] for r in records]

        selected_record = st.selectbox(
            "Select a past record",
            record_ids,
            index=None,
            placeholder="Choose a record"
        )

        if st.button("View Selected Record"):
            if selected_record is None:
                st.warning("Please select a record first")
            else:
                try:
                    history_text = view_record(
                        record_id=int(selected_record),
                        user_id=user["id"],
                        user_private_key=user["rsa_private_key"]
                    )
                    st.text_area(
                        "Medical Record",
                        history_text,
                        height=220
                    )
                except Exception:
                    st.error("Access denied or record expired")
    else:
        st.info("No medical history found")

    st.divider()

    # ==================================================
    # PRIMARY / MAIN DOCTORS
    # ==================================================
    st.subheader("👨‍⚕️ Primary Doctor(s)")

    doctors = get_patient_doctors(user["id"])

    if doctors:
        for d in doctors:
            st.markdown(
                f"- **{d['username']}** "
                f"({d['specialization'] or 'General'})"
            )
    else:
        st.info("No primary doctor assigned yet")

    st.divider()

    # ==================================================
    # REFERRAL DOCTORS
    # ==================================================
    st.subheader("🔁 Referral Doctor(s)")

    referrals = get_referral_doctors(user["id"])

    if referrals:
        for r in referrals:
            st.markdown(
                f"- **{r['username']}** "
                f"({r['specialization'] or 'General'}) "
                f"⏳ until {r['access_expires_at']}"
            )
    else:
        st.info("No active referral doctors")

    st.divider()

    # ==================================================
    # LOGOUT
    # ==================================================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
