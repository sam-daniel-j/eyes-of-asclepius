import streamlit as st

from app.services.record_service import create_record, view_record
from app.models.record_model import (
    get_doctor_all_patients,
    get_patient_records
)
from app.ui.referral_ui import referral_ui
from app.ui.emergency_ui import emergency_ui
from app.ui.access_logs_ui import access_logs_ui


def doctor_dashboard(user):
    st.title(f"🩺 Doctor Dashboard — {user['username']}")

    # ==================================================
    # CREATE MEDICAL RECORD
    # ==================================================
    st.subheader("📝 Create Medical Record")

    patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1
    )

    record_text = st.text_area(
        "Medical Record",
        placeholder="Enter diagnosis, observations, prescriptions, etc."
    )

    if st.button("Create Record"):
        if not record_text.strip():
            st.warning("Medical record cannot be empty")
        else:
            try:
                record_id = create_record(
                    plain_text=record_text,
                    patient_id=int(patient_id),
                    doctor_user=user
                )
                st.success(
                    f"Medical record created successfully (Record ID: {record_id})"
                )
            except Exception:
                st.error("Failed to create medical record")

    st.divider()

    # ==================================================
    # ALL ACCESSIBLE PATIENTS
    # ==================================================
    st.subheader("👥 My Patients")

    patients = get_doctor_all_patients(user["id"])

    if not patients:
        st.info("You currently have no patients assigned")
    else:
        patient_map = {p["username"]: p["id"] for p in patients}

        selected_patient = st.selectbox(
            "Select Patient",
            patient_map.keys(),
            index=None,
            placeholder="Choose a patient"
        )

        if selected_patient is not None:
            pid = patient_map[selected_patient]

            st.markdown(f"### 📂 Records for **{selected_patient}**")

            records = get_patient_records(pid)

            if records:
                record_ids = [r["id"] for r in records]

                selected_record = st.selectbox(
                    "Select Medical Record",
                    record_ids,
                    index=None,
                    placeholder="Choose a record"
                )

                if selected_record is not None:
                    if st.button("View Medical Record"):
                        try:
                            text = view_record(
                                record_id=int(selected_record),
                                user_id=user["id"],
                                user_private_key=user["rsa_private_key"]
                            )
                            st.text_area(
                                "Medical Record",
                                text,
                                height=260
                            )
                        except Exception:
                            st.error("Access denied or record expired")
            else:
                st.info("No medical records found for this patient")

            st.divider()

            # ==================================================
            # PATIENT ACTIONS
            # ==================================================
            st.subheader("⚙️ Patient Actions")

            referral_ui(user)
            emergency_ui(user)

    st.divider()

    # ==================================================
    # ACCESS LOGS (DOCTOR-SCOPED)
    # ==================================================
    access_logs_ui(user)

    st.divider()

    # ==================================================
    # LOGOUT
    # ==================================================
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
