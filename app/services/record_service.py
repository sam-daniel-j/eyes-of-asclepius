from typing import Dict

from app.services.assignment_service import is_doctor_assigned
from app.security.hybrid import encrypt_medical_record, decrypt_medical_record
from app.models.record_model import (
    create_medical_record,
    store_record_key,
    get_record_with_key
)
from app.models.user_model import get_user_by_id


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

    # 🔥 GET PATIENT DATA (CRITICAL FIX)
    patient_user = get_user_by_id(patient_id)

    if not patient_user:
        raise ValueError("Patient not found")

    # ==================================================
    # 🔐 ENCRYPTION RECIPIENTS (FIXED)
    # ==================================================
    recipients = {
        patient_id: patient_user["rsa_public_key"],   # ✅ patient gets correct key
        doctor_id: doctor_user["rsa_public_key"],     # ✅ doctor gets correct key
    }

    encrypted = encrypt_medical_record(
        plain_text=plain_text,
        recipient_public_keys=recipients
    )

    # ==================================================
    # STORE RECORD
    # ==================================================
    record_id = create_medical_record(
        patient_id=patient_id,
        doctor_id=doctor_id,
        encrypted_data=encrypted["encrypted_data"],
        iv=encrypted["iv"]
    )

    # ==================================================
    # STORE ENCRYPTED AES KEYS
    # ==================================================
    for user_id, enc_key in encrypted["encrypted_keys"].items():
        store_record_key(
            record_id=record_id,
            user_id=user_id,
            encrypted_aes_key=enc_key,
            granted_via="OWNER"
        )

    return record_id


# ==================================================
# VIEW RECORD
# ==================================================
def view_record(
    *,
    record_id: int,
    user_id: int,
    user_private_key: str
) -> str:
    """
    Decrypts and returns a medical record for an authorized user.
    """

    record = get_record_with_key(record_id, user_id)

    if not record:
        raise ValueError("Access denied or record not found")

    return decrypt_medical_record(
        encrypted_data=record["encrypted_data"],
        iv=record["iv"],
        encrypted_aes_key=record["encrypted_aes_key"],
        private_key_pem=user_private_key
    )


# ==================================================
# FETCH RECORDS (DOCTOR SIDE)
# ==================================================
def get_records_for_patient(patient_id: int, doctor_id: int):
    """
    Fetch records for a patient.
    Can be extended to filter by doctor if needed.
    """
    from app.models.record_model import get_patient_records

    records = get_patient_records(patient_id)

    # Optional: filter records created by this doctor
    # records = [r for r in records if r["doctor_id"] == doctor_id]

    return records