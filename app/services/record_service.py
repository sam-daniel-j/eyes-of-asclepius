from typing import Dict

from app.services.assignment_service import is_doctor_assigned
from app.database.connection import get_cursor, commit

from app.security.hybrid import encrypt_medical_record, decrypt_medical_record

from app.models.record_model import (
    create_medical_record,
    store_record_key,
    get_record_with_key,
    get_patient_records
)

from app.models.user_model import get_user_by_id


# ==================================================
# 🔐 ACCESS LOGGING (NEW)
# ==================================================
def log_access(user_id: int, patient_id: int, action: str):
    cur = get_cursor()

    cur.execute("""
        INSERT INTO access_logs (user_id, patient_id, action, timestamp)
        VALUES (%s, %s, %s, NOW())
    """, (user_id, patient_id, action))

    commit()


# ==================================================
# CREATE RECORD
# ==================================================
def create_record(
    *,
    plain_text: str,
    patient_id: int,
    doctor_user: Dict
) -> int:

    doctor_id = doctor_user["id"]

    # 🔒 SECURITY CHECK
    if not is_doctor_assigned(doctor_id, patient_id):
        raise ValueError("Doctor is not assigned to this patient")

    # 🔥 GET PATIENT
    patient_user = get_user_by_id(patient_id)

    if not patient_user:
        raise ValueError("Patient not found")

    # 🔐 ENCRYPTION RECIPIENTS
    recipients = {
        patient_id: patient_user["rsa_public_key"],
        doctor_id: doctor_user["rsa_public_key"],
    }

    encrypted = encrypt_medical_record(
        plain_text=plain_text,
        recipient_public_keys=recipients
    )

    # 🗂️ STORE RECORD
    record_id = create_medical_record(
        patient_id=patient_id,
        doctor_id=doctor_id,
        encrypted_data=encrypted["encrypted_data"],
        iv=encrypted["iv"]
    )

    # 🔑 STORE KEYS
    for user_id, enc_key in encrypted["encrypted_keys"].items():
        store_record_key(
            record_id=record_id,
            user_id=user_id,
            encrypted_aes_key=enc_key,
            granted_via="OWNER"
        )

    return record_id


# ==================================================
# VIEW RECORD (WITH LOGGING 🔥)
# ==================================================
def view_record(
    *,
    record_id: int,
    user_id: int,
    user_private_key: str
) -> str:

    record = get_record_with_key(record_id, user_id)

    if not record:
        raise ValueError("Access denied or record not found")

    # 🔓 DECRYPT
    decrypted = decrypt_medical_record(
        encrypted_data=record["encrypted_data"],
        iv=record["iv"],
        encrypted_aes_key=record["encrypted_aes_key"],
        private_key_pem=user_private_key
    )

    # 📜 LOG ACCESS
    log_access(
        user_id=user_id,
        patient_id=record["patient_id"],
        action="VIEW_RECORD"
    )

    return decrypted


# ==================================================
# FETCH RECORDS (SMART ACCESS 🔥)
# ==================================================
def get_records_for_patient(patient_id: int, doctor_id: int):
    """
    Doctor can see records if:
    - Assigned doctor
    - OR has referral access (via record_keys)
    """

    cur = get_cursor()

    # ✅ Assigned records
    assigned = is_doctor_assigned(doctor_id, patient_id)

    if assigned:
        return get_patient_records(patient_id)

    # 🔁 Referral-based access
    cur.execute("""
        SELECT mr.*
        FROM medical_records mr
        JOIN record_keys rk ON rk.record_id = mr.id
        WHERE mr.patient_id = %s AND rk.user_id = %s
    """, (patient_id, doctor_id))

    return cur.fetchall()


# ==================================================
# FETCH RECORDS (PATIENT SIDE)
# ==================================================
def get_records_for_patient_self(patient_id: int):
    """
    Patient sees all their own records
    """
    return get_patient_records(patient_id)