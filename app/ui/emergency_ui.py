import streamlit as st
from typing import Dict, Any, cast

from app.services.emergency_service import grant_emergency_access
from app.database.connection import get_cursor


def emergency_ui(doctor):
    st.subheader("🚨 Emergency Access (Break-Glass)")

    st.caption(
        "Emergency access is time-limited, audited, and only for critical situations."
    )

    # =====================================
    # INPUTS
    # =====================================
    patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1
    )

    record_id = st.number_input(
        "Medical Record ID",
        min_value=1,
        step=1
    )

    justification = st.text_area(
        "Emergency Justification",
        placeholder="Explain why immediate access is required (minimum 10 characters)"
    )

    duration = st.number_input(
        "Access Duration (minutes)",
        min_value=5,
        max_value=120,
        value=30
    )

    # =====================================
    # SUBMIT
    # =====================================
    if st.button("Grant Emergency Access"):
        if not justification or len(justification.strip()) < 10:
            st.warning("Justification must be at least 10 characters long")
            return

        # ---------------------------------
        # Fetch encrypted AES key of owner
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
        # Grant emergency access
        # ---------------------------------
        grant_emergency_access(
            record_id=int(record_id),
            patient_id=int(patient_id),
            requesting_doctor=doctor,
            encrypted_aes_key_for_owner=encrypted_key,
            justification=justification.strip(),
            duration_minutes=int(duration)
        )

        st.success(
            f"Emergency access granted for {duration} minutes and logged successfully"
        )
