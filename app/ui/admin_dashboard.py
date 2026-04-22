import streamlit as st
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt

from app.database.connection import get_cursor, commit
from app.services.assignment_service import assign_doctor_to_patient


# =========================================================
# SAFE COUNT FUNCTION (prevents None crash)
# =========================================================
def safe_count(cur, query):
    try:
        cur.execute(query)
        row = cur.fetchone()
        return row["total"] if row and "total" in row else 0
    except:
        return 0


# =========================================================
# ADMIN DASHBOARD
# =========================================================
def admin_dashboard(user):

    st.title("🛠️ Admin Control Center")

    cur = get_cursor()

    # =========================================================
    # 👤 USER MANAGEMENT
    # =========================================================
    st.header("👤 User Management")

    col1, col2 = st.columns(2)

    # -------- CREATE USER --------
    with col1:
        st.subheader("➕ Create User")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["doctor", "patient", "admin"])
        specialization = st.text_input("Specialization (doctor only)")

        if st.button("Create User"):
            if not username or not password:
                st.warning("Fill all fields")
            else:
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                cur.execute("""
                    INSERT INTO users (username, password_hash, role, specialization)
                    VALUES (%s, %s, %s, %s)
                """, (
                    username,
                    hashed,
                    role,
                    specialization if role == "doctor" else None
                ))

                commit()
                st.success("User created successfully")

    # -------- DELETE USER --------
    with col2:
        st.subheader("🗑️ Delete User")

        cur.execute("SELECT id, username, role FROM users")
        users = cur.fetchall()

        if users:
            user_map = {
                f"{u['id']} - {u['username']} ({u['role']})": u["id"]
                for u in users
            }

            selected_user = st.selectbox("Select User", user_map.keys())

            if st.button("Delete User"):
                cur.execute("DELETE FROM users WHERE id=%s", (user_map[selected_user],))
                commit()
                st.success("User deleted")

    st.divider()

    # =========================================================
    # 👥 ASSIGNMENT
    # =========================================================
    st.header("👥 Doctor–Patient Assignment")

    cur.execute("SELECT id, username, public_id FROM users WHERE role='doctor'")
    doctors = cur.fetchall()

    cur.execute("SELECT id, username, public_id FROM users WHERE role='patient'")
    patients = cur.fetchall()

    if doctors and patients:

        doctor_map = {
            f"{d['public_id']} - {d['username']}": d["id"]
            for d in doctors
        }

        patient_map = {
            f"{p['public_id']} - {p['username']}": p["id"]
            for p in patients
        }

        col1, col2 = st.columns(2)

        with col1:
            selected_doc = st.selectbox("Doctor", doctor_map.keys())

        with col2:
            selected_pat = st.selectbox("Patient", patient_map.keys())

        col3, col4 = st.columns(2)

        with col3:
            if st.button("Assign Doctor"):
                assign_doctor_to_patient(
                    doctor_map[selected_doc],
                    patient_map[selected_pat]
                )
                st.success("Doctor assigned")

        with col4:
            if st.button("Remove Doctor"):
                cur.execute("""
                    DELETE FROM doctor_patient_map
                    WHERE doctor_id=%s AND patient_id=%s
                """, (doctor_map[selected_doc], patient_map[selected_pat]))
                commit()
                st.success("Doctor removed")

    # CURRENT ASSIGNMENTS
    st.subheader("📋 Current Assignments")

    cur.execute("""
        SELECT d.username AS doctor, p.username AS patient
        FROM doctor_patient_map m
        JOIN users d ON d.id = m.doctor_id
        JOIN users p ON p.id = m.patient_id
    """)

    assignments = cur.fetchall()

    if assignments:
        st.dataframe(assignments, use_container_width=True)
    else:
        st.info("No assignments yet")

    st.divider()

    # =========================================================
    # 📊 ANALYTICS
    # =========================================================
    st.header("📊 System Analytics")

    total_records = safe_count(cur, "SELECT COUNT(*) AS total FROM medical_records")
    total_users = safe_count(cur, "SELECT COUNT(*) AS total FROM users")
    total_referrals = safe_count(cur, "SELECT COUNT(*) AS total FROM doctor_referrals")

    col1, col2, col3 = st.columns(3)

    col1.metric("📁 Records", total_records)
    col2.metric("👥 Users", total_users)
    col3.metric("🔁 Referrals", total_referrals)

    st.divider()

    # -------- RECORDS PER DOCTOR --------
    st.subheader("👨‍⚕️ Records per Doctor")

    cur.execute("""
        SELECT u.username, COUNT(*) AS count
        FROM medical_records m
        JOIN users u ON u.id = m.created_by_doctor_id
        GROUP BY u.username
    """)

    data = cur.fetchall()

    if data:
        df = pd.DataFrame(data)

        fig, ax = plt.subplots(figsize=(4, 2.5))  # 🔥 smaller graph
        ax.bar(df["username"], df["count"])

        ax.set_xticks(range(len(df["username"])))
        ax.set_xticklabels(df["username"], rotation=30, ha='right')

        st.pyplot(fig, use_container_width=False)
    else:
        st.info("No doctor data")

    # -------- RECORDS PER PATIENT --------
    st.subheader("🧑 Patient Activity")

    cur.execute("""
        SELECT u.username, COUNT(*) AS count
        FROM medical_records m
        JOIN users u ON u.id = m.patient_id
        GROUP BY u.username
    """)

    data = cur.fetchall()

    if data:
        df = pd.DataFrame(data)

        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.bar(df["username"], df["count"])

        ax.set_xticks(range(len(df["username"])))
        ax.set_xticklabels(df["username"], rotation=30, ha='right')

        st.pyplot(fig, use_container_width=False)
    else:
        st.info("No patient data")

    # -------- ACCESS TREND --------
    st.subheader("📜 Access Activity")

    cur.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as count
        FROM access_logs
        GROUP BY day
        ORDER BY day
    """)

    logs = cur.fetchall()

    if logs:
        df = pd.DataFrame(logs)

        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.plot(df["day"], df["count"], marker='o')

        st.pyplot(fig, use_container_width=False)
    else:
        st.info("No access logs yet")

    st.divider()

    # =========================================================
    # 🔁 REFERRALS
    # =========================================================
    st.header("🔁 Referral Management")

    cur.execute("""
        SELECT 
            r.id,
            p.username AS patient,
            d1.username AS from_doctor,
            d2.username AS to_doctor,
            r.reason,
            r.is_active
        FROM doctor_referrals r
        JOIN users p ON p.id = r.patient_id
        JOIN users d1 ON d1.id = r.from_doctor_id
        JOIN users d2 ON d2.id = r.to_doctor_id
        ORDER BY r.id DESC
    """)

    referrals = cur.fetchall()

    if referrals:
        st.dataframe(referrals, use_container_width=True)
    else:
        st.info("No referrals yet")

    ref_id = st.number_input("Referral ID", min_value=1)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Revoke Referral"):
            cur.execute("UPDATE doctor_referrals SET is_active=FALSE WHERE id=%s", (ref_id,))
            commit()
            st.success("Referral revoked")

    with col2:
        if st.button("Delete Referral"):
            cur.execute("DELETE FROM doctor_referrals WHERE id=%s", (ref_id,))
            commit()
            st.success("Referral deleted")

    st.divider()

    # =========================================================
    # 📜 ACCESS LOGS
    # =========================================================
    st.header("📜 Access Logs")

    cur.execute("""
        SELECT user_id, patient_id, action, timestamp
        FROM access_logs
        ORDER BY timestamp DESC
        LIMIT 200
    """)

    logs = cur.fetchall()

    if logs:
        st.dataframe(logs, use_container_width=True)
    else:
        st.info("No logs yet")

    st.divider()

    # =========================================================
    # 🚪 LOGOUT
    # =========================================================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()