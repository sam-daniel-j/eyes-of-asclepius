from app.database.connection import get_cursor, commit
from app.models.record_model import store_record_key


def refer_patient(
    patient_id: int,
    from_doctor: dict,
    to_doctor_id: int,
    record_id: int,
    encrypted_aes_key_for_from_doctor: str,
    reason: str
):
    """
    Grant PERMANENT referral access to another doctor.
    Referral access is NOT time-limited and remains active
    until explicitly revoked by admin.
    """

    cur = get_cursor()

    # --------------------------------------------------
    # Insert referral entry (NO EXPIRY)
    # --------------------------------------------------
    cur.execute(
        """
        INSERT INTO doctor_referrals
        (
            patient_id,
            from_doctor_id,
            to_doctor_id,
            record_id,
            encrypted_aes_key,
            reason,
            is_active,
            access_expires_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, TRUE, NULL);
        """,
        (
            patient_id,
            from_doctor["id"],
            to_doctor_id,
            record_id,
            encrypted_aes_key_for_from_doctor,
            reason
        )
    )

    # --------------------------------------------------
    # Grant record key to referred doctor
    # (permanent access, no expiry)
    # --------------------------------------------------
    store_record_key(
        record_id=record_id,
        user_id=to_doctor_id,
        encrypted_aes_key=encrypted_aes_key_for_from_doctor,
        granted_via="REFERRAL",
        expires_at=None
    )

    commit()
