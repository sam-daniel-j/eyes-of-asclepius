from typing import Dict, Any, List, Optional, cast
from datetime import datetime

from app.database.connection import get_cursor, commit


# ======================================================
# MEDICAL RECORD CREATION
# ======================================================

def create_medical_record(
    patient_id: int,
    doctor_id: int,
    encrypted_data: str,
    iv: str
) -> int:
    cur = get_cursor()
    cur.execute(
        """
        INSERT INTO medical_records
        (patient_id, created_by_doctor_id, encrypted_data, iv)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """,
        (patient_id, doctor_id, encrypted_data, iv)
    )

    row = cast(Dict[str, Any], cur.fetchone())
    commit()
    return row["id"]


# ======================================================
# RECORD KEYS (ACCESS CONTROL)
# ======================================================

def store_record_key(
    record_id: int,
    user_id: int,
    encrypted_aes_key: str,
    granted_via: str,
    expires_at: Optional[datetime] = None
):
    cur = get_cursor()
    cur.execute(
        """
        INSERT INTO record_keys
        (record_id, user_id, encrypted_aes_key, granted_via, expires_at)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (record_id, user_id, encrypted_aes_key, granted_via, expires_at)
    )
    commit()


def get_record_with_key(
    record_id: int,
    user_id: int
) -> Optional[Dict[str, Any]]:
    cur = get_cursor()
    cur.execute(
        """
        SELECT
            mr.encrypted_data,
            mr.iv,
            rk.encrypted_aes_key
        FROM medical_records mr
        JOIN record_keys rk ON rk.record_id = mr.id
        WHERE mr.id = %s
          AND rk.user_id = %s
          AND (rk.expires_at IS NULL OR rk.expires_at > NOW());
        """,
        (record_id, user_id)
    )

    row = cur.fetchone()
    return cast(Dict[str, Any], row) if row else None


# ======================================================
# PATIENT-SIDE HELPERS
# ======================================================

def get_patient_records(patient_id: int) -> List[Dict[str, Any]]:
    cur = get_cursor()
    cur.execute(
        """
        SELECT id, created_at
        FROM medical_records
        WHERE patient_id = %s
        ORDER BY created_at DESC;
        """,
        (patient_id,)
    )
    return cast(List[Dict[str, Any]], cur.fetchall())


def get_latest_record(patient_id: int) -> Optional[Dict[str, Any]]:
    cur = get_cursor()
    cur.execute(
        """
        SELECT id
        FROM medical_records
        WHERE patient_id = %s
        ORDER BY created_at DESC
        LIMIT 1;
        """,
        (patient_id,)
    )
    row = cur.fetchone()
    return cast(Dict[str, Any], row) if row else None


def get_patient_doctors(patient_id: int) -> List[Dict[str, Any]]:
    cur = get_cursor()
    cur.execute(
        """
        SELECT DISTINCT
            u.username,
            u.specialization
        FROM medical_records mr
        JOIN users u ON u.id = mr.created_by_doctor_id
        WHERE mr.patient_id = %s;
        """,
        (patient_id,)
    )
    return cast(List[Dict[str, Any]], cur.fetchall())


def get_referral_doctors(patient_id: int) -> List[Dict[str, Any]]:
    cur = get_cursor()
    cur.execute(
        """
        SELECT
            u.username,
            u.specialization
        FROM doctor_referrals dr
        JOIN users u ON u.id = dr.to_doctor_id
        WHERE dr.patient_id = %s
          AND dr.is_active = TRUE;
        """,
        (patient_id,)
    )
    return cast(List[Dict[str, Any]], cur.fetchall())


# ======================================================
# DOCTOR-SIDE HELPERS (ALL ACCESS TYPES)
# ======================================================

def get_doctor_all_patients(doctor_id: int) -> List[Dict[str, Any]]:
    """
    Returns patients for whom the doctor has access via:
    - Ownership
    - Permanent referral
    - Time-limited emergency access
    """
    cur = get_cursor()
    cur.execute(
        """
        SELECT DISTINCT
            u.id,
            u.username
        FROM users u
        WHERE u.id IN (

            -- Patients where doctor created records
            SELECT patient_id
            FROM medical_records
            WHERE created_by_doctor_id = %s

            UNION

            -- Permanent referrals
            SELECT patient_id
            FROM doctor_referrals
            WHERE to_doctor_id = %s
              AND is_active = TRUE

            UNION

            -- Emergency access (time-limited)
            SELECT mr.patient_id
            FROM record_keys rk
            JOIN medical_records mr ON mr.id = rk.record_id
            WHERE rk.user_id = %s
              AND rk.granted_via = 'EMERGENCY'
              AND (rk.expires_at IS NULL OR rk.expires_at > NOW())
        );
        """,
        (doctor_id, doctor_id, doctor_id)
    )

    return cast(List[Dict[str, Any]], cur.fetchall())
