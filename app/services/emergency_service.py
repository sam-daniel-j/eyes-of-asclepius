from datetime import datetime, timedelta
from typing import Dict

from app.models.record_model import store_record_key
from app.models.user_model import get_user_by_id
from app.security.rsa import encrypt_with_public_key
from app.services.access_log_service import record_log


def grant_emergency_access(
    *,
    record_id: int,
    patient_id: int,
    requesting_doctor: Dict,
    encrypted_aes_key_for_owner: str,
    justification: str,
    duration_minutes: int = 30
):
    """
    Grants short-lived emergency access to a medical record.
    """

    if requesting_doctor["role"] != "doctor":
        raise ValueError("Only doctors can request emergency access")

    if not justification or len(justification.strip()) < 10:
        raise ValueError("Emergency access requires proper justification")

    expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)

    # Encrypt AES key for requesting doctor
    encrypted_key = encrypt_with_public_key(
        data=encrypted_aes_key_for_owner.encode("utf-8"),
        public_key_pem=requesting_doctor["rsa_public_key"]
    )

    store_record_key(
        record_id=record_id,
        user_id=requesting_doctor["id"],
        encrypted_aes_key=encrypted_key,
        granted_via="EMERGENCY",
        expires_at=expires_at
    )

    # Log the emergency access
    record_log(
        user_id=requesting_doctor["id"],
        patient_id=patient_id,
        action="EMERGENCY_ACCESS",
        justification=justification
    )
