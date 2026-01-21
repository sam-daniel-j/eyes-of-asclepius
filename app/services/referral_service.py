from datetime import datetime, timedelta
from typing import Dict

from app.models.referral_model import create_referral, get_active_referral
from app.models.record_model import store_record_key
from app.models.user_model import get_user_by_id
from app.security.rsa import encrypt_with_public_key


def refer_patient(
    *,
    patient_id: int,
    from_doctor: Dict,
    to_doctor_id: int,
    record_id: int,
    encrypted_aes_key_for_from_doctor: str,
    reason: str,
    duration_hours: int = 24
) -> int:
    """
    Grants temporary access to another doctor via referral.
    """

    # -------------------------
    # Validate target doctor
    # -------------------------
    to_doctor = get_user_by_id(to_doctor_id)
    if not to_doctor or to_doctor["role"] != "doctor":
        raise ValueError("Invalid target doctor")

    # -------------------------
    # Create referral entry
    # -------------------------
    expires_at = datetime.utcnow() + timedelta(hours=duration_hours)

    referral_id = create_referral(
        patient_id=patient_id,
        from_doctor_id=from_doctor["id"],
        to_doctor_id=to_doctor_id,
        reason=reason,
        access_expires_at=expires_at
    )

    # -------------------------
    # Re-encrypt AES key for referred doctor
    # -------------------------
    encrypted_key_for_referred = encrypt_with_public_key(
        data=encrypted_aes_key_for_from_doctor.encode("utf-8"),
        public_key_pem=to_doctor["rsa_public_key"]
    )

    store_record_key(
        record_id=record_id,
        user_id=to_doctor_id,
        encrypted_aes_key=encrypted_key_for_referred,
        granted_via="REFERRAL",
        expires_at=expires_at
    )

    return referral_id


def check_referral_access(patient_id: int, doctor_id: int) -> bool:
    """
    Checks if a doctor has active referral access to a patient.
    """
    referral = get_active_referral(patient_id, doctor_id)
    return referral is not None
