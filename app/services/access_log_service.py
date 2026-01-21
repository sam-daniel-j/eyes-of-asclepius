from typing import Optional
from app.models.access_log_model import log_access


def record_log(
    *,
    user_id: int,
    action: str,
    patient_id: Optional[int] = None,
    justification: Optional[str] = None
):
    log_access(
        user_id=user_id,
        patient_id=patient_id,
        action=action,
        justification=justification
    )
