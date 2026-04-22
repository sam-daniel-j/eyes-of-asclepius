import streamlit as st
from datetime import datetime, timedelta

from app.services.record_service import create_record, view_record, get_records_for_patient
from app.services.assignment_service import get_all_patients_for_doctor
from app.models.record_model import get_record_with_key, store_record_key
from app.services.referral_service import refer_patient
from app.models.user_model import get_user_by_id
from app.database.connection import get_cursor
from app.security.rsa import decrypt_with_private_key, encrypt_with_public_key


def doctor_dashboard(user):

    # ================= LOAD PATIENTS =================
    patients = get_all_patients_for_doctor(user["id"])

    # ================= SIDEBAR =================
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        st.button("🏠 Home", use_container_width=True)
        st.button("👥 My Patients", use_container_width=True)
        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ================= HEADER =================
    st.markdown(f"## 👨‍⚕️ Doctor Dashboard - Dr. {user['username']}")

    # ================= PATIENT SELECT =================
    if not patients:
        st.warning("No patients assigned or referred")
        return

    patient_display = {
        f"{p['public_id']} - {p['username']} ({p['type']})": p["id"]
        for p in patients
    }

    selected_patient = st.selectbox("Select Patient", list(patient_display.keys()))

    if not selected_patient:
        return

    pid = patient_display[selected_patient]

    # ================= RECORDS =================
    records = get_records_for_patient(pid, user["id"])

    st.markdown("### 📄 Records")

    if records:
        for r in records:
            if st.button(f"View Record #{r['id']}", key=f"view_{r['id']}"):

                try:
                    text = view_record(
                        record_id=r["id"],
                        user_id=user["id"],
                        user_private_key=user["rsa_private_key"]
                    )

                    st.text_area("Record", text)

                except Exception as e:
                    st.error(f"Decryption failed: {str(e)}")

    else:
        st.info("No records available")

    # ================= ADD RECORD =================
    st.markdown("### ➕ Add Record")

    new_record = st.text_area("New Record")

    if st.button("Add Record"):

        if not new_record.strip():
            st.warning("Enter record")
            return

        try:
            create_record(
                plain_text=new_record,
                patient_id=pid,
                doctor_user=user
            )

            st.success("Record added successfully")
            st.rerun()

        except Exception as e:
            st.error(f"Error adding record: {str(e)}")

    # ================= LOAD DOCTORS =================
    cur = get_cursor()
    cur.execute("SELECT id, username, public_id FROM users WHERE role='doctor'")
    doctors = cur.fetchall()

    doctor_map = {
        f"{d['public_id']} - {d['username']}": d["id"]
        for d in doctors if d["id"] != user["id"]
    }

    # ================= REFERRAL =================
    st.markdown("### 🔁 Referral")

    ref_doc = st.selectbox("Select Doctor", list(doctor_map.keys()), index=None)
    reason = st.text_area("Reason for referral")

    if st.button("Refer Patient"):

        if not ref_doc:
            st.warning("Select doctor")
            return

        if not records:
            st.warning("No records available")
            return

        try:
            to_doc_id = doctor_map[ref_doc]
            record_id = records[0]["id"]

            record = get_record_with_key(record_id, user["id"])

            if not record:
                st.error("You don't have access to this record")
                return

            aes_key = decrypt_with_private_key(
                record["encrypted_aes_key"],
                user["rsa_private_key"]
            )

            to_doc = get_user_by_id(to_doc_id)

            if not to_doc or not to_doc.get("rsa_public_key"):
                st.error("Target doctor has no public key")
                return

            encrypted_key = encrypt_with_public_key(
                aes_key,
                to_doc["rsa_public_key"]
            )

            refer_patient(
                patient_id=pid,
                from_doctor=user,
                to_doctor_id=to_doc_id,
                record_id=record_id,
                encrypted_aes_key_for_from_doctor=encrypted_key,
                reason=reason
            )

            st.success("Referral successful")

        except Exception as e:
            st.error(f"Referral failed: {str(e)}")

    # ================= EMERGENCY =================
    st.markdown("### 🚨 Emergency Access")

    em_doc = st.selectbox("Emergency Doctor", list(doctor_map.keys()), index=None)

    if st.button("Grant Emergency Access"):

        if not em_doc:
            st.warning("Select doctor")
            return

        if not records:
            st.warning("No records available")
            return

        try:
            to_doc_id = doctor_map[em_doc]
            record_id = records[0]["id"]

            record = get_record_with_key(record_id, user["id"])

            if not record:
                st.error("No access to record")
                return

            aes_key = decrypt_with_private_key(
                record["encrypted_aes_key"],
                user["rsa_private_key"]
            )

            to_doc = get_user_by_id(to_doc_id)

            if not to_doc or not to_doc.get("rsa_public_key"):
                st.error("Doctor has no public key")
                return

            encrypted_key = encrypt_with_public_key(
                aes_key,
                to_doc["rsa_public_key"]
            )

            store_record_key(
                record_id=record_id,
                user_id=to_doc_id,
                encrypted_aes_key=encrypted_key,
                granted_via="EMERGENCY",
                expires_at=datetime.now() + timedelta(minutes=10)
            )

            st.success("Emergency access granted (10 mins)")

        except Exception as e:
            st.error(f"Emergency access failed: {str(e)}")