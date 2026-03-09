import streamlit as st
from app.database.connection import get_cursor


def access_logs_ui(user):
    st.subheader("📜 Access Logs")

    cur = get_cursor()


    if user["role"] == "admin":
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
        st.caption("Showing latest 200 system-wide access events")


    else:
        cur.execute(
            """
            SELECT
                user_id,
                patient_id,
                action,
                justification,
                timestamp
            FROM access_logs
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 100;
            """,
            (user["id"],)
        )
        logs = cur.fetchall()
        st.caption("Showing your latest 100 access events")

    if not logs:
        st.info("No access logs available")
        return

    st.dataframe(
        logs,
        use_container_width=True,
        hide_index=True
    )
