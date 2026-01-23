import streamlit as st
from typing import Dict, Any, cast

from app.models.user_model import get_user_by_id
from app.models.record_model import get_patient_records
from app.services.referral_service import refer_patient
from app.database.connection import get_cursor


def referral_ui(doctor):
    st.subheader("🔁 Refer Patient to Another Doctor")

    # =====================================
    # PATIENT SELECTION
    # =====================================
    patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1
    )

    if not patient_id:
        return

    records = get_patient_records(int(patient_id))
    if not records:
        st.info("No medical records found for this patient")
        return

    record_id = st.selectbox(
        "Select Medical Record",
        [r["id"] for r in records],
        index=None,
        placeholder="Choose a record"
    )

    if record_id is None:
        return

    # =====================================
    # TARGET DOCTOR
    # =====================================
    to_doctor_id = st.number_input(
        "Refer To Doctor ID",
        min_value=1,
        step=1
    )

    if not to_doctor_id:
        return

    target_doctor = get_user_by_id(int(to_doctor_id))
    if not target_doctor or target_doctor["role"] != "doctor":
        st.error("Invalid doctor ID")
        return

    st.caption(
        f"Target Doctor: {target_doctor['username']} "
        f"({target_doctor.get('specialization') or 'General'})"
    )

    # =====================================
    # REFERRAL DETAILS
    # =====================================
    reason = st.text_area(
        "Referral Reason",
        placeholder="Reason for referral (required)"
    )

    st.caption("ℹ️ Referral access is permanent until revoked by an admin.")

    # =====================================
    # SUBMIT
    # =====================================
    if st.button("Grant Referral Access"):
        if not reason.strip():
            st.warning("Referral reason is required")
            return

        # ---------------------------------
        # Fetch encrypted AES key (owner)
        # ---------------------------------
        cur = get_cursor()
        cur.execute(
            """
            SELECT encrypted_aes_key
            FROM record_keys
            WHERE record_id = %s AND user_id = %s;
            """,
            (int(record_id), doctor["id"])
        )

        row = cur.fetchone()
        if row is None:
            st.error("You do not have ownership access to this record")
            return

        encrypted_key = cast(Dict[str, Any], row)["encrypted_aes_key"]

        # ---------------------------------
        # Grant referral
        # ---------------------------------
        refer_patient(
            patient_id=int(patient_id),
            from_doctor=doctor,
            to_doctor_id=int(to_doctor_id),
            record_id=int(record_id),
            encrypted_aes_key_for_from_doctor=encrypted_key,
            reason=reason
        )

        st.success("Referral access granted permanently")
