from app.services.user_service import register_user
from app.services.auth_service import authenticate_user
from app.services.record_service import create_record, view_record

def test_record_flow():
    register_user("doc_flow", "123", "doctor", "General")
    register_user("pat_flow", "123", "patient")

    doctor = authenticate_user("doc_flow", "123")
    patient = authenticate_user("pat_flow", "123")

    record_id = create_record(
        plain_text="Test medical data",
        patient_id=patient["id"],
        doctor_user=doctor
    )

    text = view_record(
        record_id=record_id,
        user_id=patient["id"],
        user_private_key=patient["rsa_private_key"]
    )

    assert text == "Test medical data"
