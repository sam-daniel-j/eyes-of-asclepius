from app.database.connection import get_cursor, commit
from app.models.record_model import (
    create_medical_record,
    store_record_key,
    get_record_with_key,
    get_patient_records
)
from app.models.user_model import get_user_by_id
from app.security.hybrid import encrypt_medical_record, decrypt_medical_record


# ==============================
# CREATE RECORD
# ==============================
def create_record(plain_text, patient_id, doctor_user):

    doctor_id = doctor_user["id"]
    patient = get_user_by_id(patient_id)

    if not patient:
        raise ValueError("Patient not found")

    if not patient.get("rsa_public_key") or not doctor_user.get("rsa_public_key"):
        raise ValueError("Missing RSA keys")

    recipients = {
        patient_id: patient["rsa_public_key"],
        doctor_id: doctor_user["rsa_public_key"]
    }

    encrypted = encrypt_medical_record(
        plain_text=plain_text,
        recipient_public_keys=recipients
    )

    record_id = create_medical_record(
        patient_id,
        doctor_id,
        encrypted["encrypted_data"],
        encrypted["iv"]
    )

    # 🔥 store AES key for BOTH users
    for uid, enc_key in encrypted["encrypted_keys"].items():
        store_record_key(record_id, uid, enc_key, "OWNER")

    return record_id


# ==============================
# VIEW RECORD
# ==============================
def view_record(record_id, user_id, user_private_key):

    record = get_record_with_key(record_id, user_id)

    if not record:
        raise ValueError("Access denied or record not found")

    decrypted = decrypt_medical_record(
        encrypted_data=record["encrypted_data"],
        iv=record["iv"],
        encrypted_aes_key=record["encrypted_aes_key"],
        private_key_pem=user_private_key
    )

    return decrypted


# ==============================
# GET RECORDS FOR PATIENT (UI FIX)
# ==============================
def get_records_for_patient(patient_id, user_id):

    records = get_patient_records(patient_id)

    cur = get_cursor()

    accessible_records = []

    for r in records:
        cur.execute("""
            SELECT 1
            FROM record_keys
            WHERE record_id = %s
              AND user_id = %s
              AND (expires_at IS NULL OR expires_at > NOW())
        """, (r["id"], user_id))

        if cur.fetchone():
            accessible_records.append(r)

    return accessible_records