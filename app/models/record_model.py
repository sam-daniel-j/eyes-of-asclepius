from typing import Dict, Any, List, Optional, cast
from app.database.connection import get_cursor, commit
from datetime import datetime
from typing import Optional


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


def get_record_with_key(record_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    cur = get_cursor()
    cur.execute(
        """
        SELECT
            mr.encrypted_data,
            mr.iv,
            rk.encrypted_aes_key
        FROM medical_records mr
        JOIN record_keys rk ON rk.record_id = mr.id
        WHERE mr.id = %s AND rk.user_id = %s;
        """,
        (record_id, user_id)
    )

    row = cur.fetchone()
    if row is None:
        return None

    return cast(Dict[str, Any], row)


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

    rows = cur.fetchall()
    return cast(List[Dict[str, Any]], rows)
