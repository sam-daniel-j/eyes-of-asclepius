# app/services/referral_service.py

from datetime import datetime
from app.database.connection import get_cursor
from app.models.record_model import store_record_key


# =========================================================
# 🔁 REFER PATIENT (MAIN FUNCTION)
# =========================================================
def refer_patient(
    *,
    patient_id: int,
    from_doctor: dict,
    to_doctor_id: int,
    record_id: int,
    encrypted_aes_key_for_from_doctor: str,
    reason: str
):
    """
    Creates referral AND grants access to the receiving doctor.
    """

    cur = get_cursor()

    # ================= CHECK IF ALREADY REFERRED =================
    cur.execute("""
        SELECT id FROM doctor_referrals
        WHERE patient_id = %s
        AND to_doctor_id = %s
        AND record_id = %s
        AND is_active = TRUE
    """, (patient_id, to_doctor_id, record_id))

    existing = cur.fetchone()

    if existing:
        return False  # already referred

    # ================= INSERT REFERRAL =================
    cur.execute("""
        INSERT INTO doctor_referrals (
            patient_id,
            from_doctor_id,
            to_doctor_id,
            record_id,
            reason,
            created_at,
            is_active
        )
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
    """, (
        patient_id,
        from_doctor["id"],
        to_doctor_id,
        record_id,
        reason,
        datetime.now()
    ))

    # ================= 🔥 GRANT ACCESS =================
    store_record_key(
        record_id=record_id,
        user_id=to_doctor_id,
        encrypted_aes_key=encrypted_aes_key_for_from_doctor,
        granted_via="REFERRAL"
    )

    return True


# =========================================================
# 📋 GET REFERRALS FOR A DOCTOR
# =========================================================
def get_referrals_for_doctor(doctor_id):
    """
    Returns all active referrals received by a doctor
    """

    cur = get_cursor()

    cur.execute("""
        SELECT r.id,
               r.patient_id,
               u.username AS patient_name,
               u.public_id,
               r.from_doctor_id,
               d.username AS from_doctor_name,
               r.record_id,
               r.reason,
               r.created_at
        FROM doctor_referrals r
        JOIN users u ON u.id = r.patient_id
        JOIN users d ON d.id = r.from_doctor_id
        WHERE r.to_doctor_id = %s
        AND r.is_active = TRUE
        ORDER BY r.created_at DESC
    """, (doctor_id,))

    return cur.fetchall()


# =========================================================
# ❌ REVOKE REFERRAL
# =========================================================
def revoke_referral(referral_id):
    """
    Deactivates referral (soft delete)
    """

    cur = get_cursor()

    cur.execute("""
        UPDATE doctor_referrals
        SET is_active = FALSE
        WHERE id = %s
    """, (referral_id,))

    return True


# =========================================================
# 🔍 CHECK IF DOCTOR HAS REFERRAL ACCESS
# =========================================================
def has_referral_access(doctor_id, record_id):
    """
    Checks if doctor has referral access to a record
    """

    cur = get_cursor()

    cur.execute("""
        SELECT id FROM doctor_referrals
        WHERE to_doctor_id = %s
        AND record_id = %s
        AND is_active = TRUE
    """, (doctor_id, record_id))

    return cur.fetchone() is not None