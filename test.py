from app.services.record_service import create_record

record_id = create_record(
    plain_text="Patient diagnosed with flu.",
    patient_id=patient_id,
    doctor_user=doctor
)

print(record_id)
