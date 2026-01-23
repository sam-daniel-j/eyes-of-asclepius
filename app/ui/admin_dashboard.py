import streamlit as st
from typing import Dict, Any, cast

from app.database.connection import get_cursor, commit


def admin_dashboard(user):
    st.title("🛠️ Admin Dashboard")

    cur = get_cursor()

    # ==================================================
    # USERS MANAGEMENT
    # ==================================================
    st.subheader("👤 All Users")

    cur.execute(
        """
        SELECT id, username, role, specialization
        FROM users
        ORDER BY id;
        """
    )
    users = cur.fetchall()
    st.dataframe(users, use_container_width=True)

    st.divider()

    # ==================================================
    # MEDICAL RECORDS OVERVIEW
    # ==================================================
    st.subheader("🏥 Medical Records")

    cur.execute(
        """
        SELECT
            id,
            patient_id,
            created_by_doctor_id,
            created_at
        FROM medical_records
        ORDER BY created_at DESC;
        """
    )
    records = cur.fetchall()
    st.dataframe(records, use_container_width=True)

    st.divider()

    # ==================================================
    # REFERRAL MANAGEMENT (REVOKE)
    # ==================================================
    st.subheader("🔁 Doctor Referrals")

    cur.execute(
        """
        SELECT
            id,
            patient_id,
            from_doctor_id,
            to_doctor_id,
            record_id,
            reason,
            is_active
        FROM doctor_referrals
        ORDER BY id DESC;
        """
    )
    referrals = cur.fetchall()
    st.dataframe(referrals, use_container_width=True)

    referral_id = st.number_input(
        "Referral ID to revoke",
        min_value=1,
        step=1
    )

    if st.button("Revoke Referral"):
        cur.execute(
            """
            UPDATE doctor_referrals
            SET is_active = FALSE
            WHERE id = %s;
            """,
            (int(referral_id),)
        )

        # Also remove record key access
        cur.execute(
            """
            DELETE FROM record_keys
            WHERE record_id = (
                SELECT record_id FROM doctor_referrals WHERE id = %s
            )
            AND user_id = (
                SELECT to_doctor_id FROM doctor_referrals WHERE id = %s
            );
            """,
            (int(referral_id), int(referral_id))
        )

        commit()
        st.success("Referral access revoked")

    st.divider()

    # ==================================================
    # ACCESS LOGS (SYSTEM-WIDE)
    # ==================================================
    st.subheader("📜 Access Logs")

    cur.execute(
        """
        SELECT
            user_id,
            patient_id,
            action,
            justification,
            timestamp
        FROM access_logs
        ORDER BY timestamp DESC
        LIMIT 200;
        """
    )
    logs = cur.fetchall()
    st.dataframe(logs, use_container_width=True)

    st.divider()

    # ==================================================
    # LOGOUT
    # ==================================================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
