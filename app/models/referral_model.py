from typing import Dict, Any, Optional, cast
from datetime import datetime

from app.database.connection import get_cursor, commit


def create_referral(
    patient_id: int,
    from_doctor_id: int,
    to_doctor_id: int,
    reason: str,
    access_expires_at: datetime
) -> int:
    cur = get_cursor()

    cur.execute(
        """
        INSERT INTO doctor_referrals
        (patient_id, from_doctor_id, to_doctor_id, reason, access_expires_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (
            patient_id,
            from_doctor_id,
            to_doctor_id,
            reason,
            access_expires_at
        )
    )

    row = cast(Dict[str, Any], cur.fetchone())
    commit()
    return row["id"]


def get_active_referral(
    patient_id: int,
    to_doctor_id: int
) -> Optional[Dict[str, Any]]:
    cur = get_cursor()

    cur.execute(
        """
        SELECT *
        FROM doctor_referrals
        WHERE patient_id = %s
          AND to_doctor_id = %s
          AND is_active = TRUE
          AND access_expires_at > NOW();
        """,
        (patient_id, to_doctor_id)
    )

    row = cur.fetchone()
    if row is None:
        return None

    return cast(Dict[str, Any], row)


def deactivate_referral(referral_id: int):
    cur = get_cursor()
    cur.execute(
        """
        UPDATE doctor_referrals
        SET is_active = FALSE
        WHERE id = %s;
        """,
        (referral_id,)
    )
    commit()
