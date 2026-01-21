from typing import Optional
from app.database.connection import get_cursor, commit


def log_access(
    *,
    user_id: int,
    patient_id: Optional[int],
    action: str,
    justification: Optional[str] = None
):
    cur = get_cursor()
    cur.execute(
        """
        INSERT INTO access_logs
        (user_id, patient_id, action, justification)
        VALUES (%s, %s, %s, %s);
        """,
        (user_id, patient_id, action, justification)
    )
    commit()
