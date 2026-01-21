from typing import Dict

from app.security.hybrid import encrypt_medical_record, decrypt_medical_record
from app.models.record_model import (
    create_medical_record,
    store_record_key,
    get_record_with_key
)


def create_record(
    *,
    plain_text: str,
    patient_id: int,
    doctor_user: Dict
) -> int:
    """
    Creates a new encrypted medical record.

    doctor_user must be the authenticated doctor object.
    """

    # Recipients: patient + doctor
    recipients = {
        patient_id: doctor_user["rsa_public_key"],
        doctor_user["id"]: doctor_user["rsa_public_key"],
    }

    encrypted = encrypt_medical_record(
        plain_text=plain_text,
        recipient_public_keys=recipients
    )

    # Store encrypted record
    record_id = create_medical_record(
        patient_id=patient_id,
        doctor_id=doctor_user["id"],
        encrypted_data=encrypted["encrypted_data"],
        iv=encrypted["iv"]
    )

    # Store AES keys
    for user_id, enc_key in encrypted["encrypted_keys"].items():
        store_record_key(
            record_id=record_id,
            user_id=user_id,
            encrypted_aes_key=enc_key,
            granted_via="OWNER"
        )

    return record_id


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
