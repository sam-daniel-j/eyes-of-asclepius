from app.services.assignment_service import assign_doctor_to_patient, get_doctor_patients
from app.services.user_service import create_user

# Create sample users
doc = create_user("doc_test", "1234", "doctor")
print("Doctor:", doc)

pat = create_user("pat_test", "1234", "patient")
print("Patient:", pat)

assign_doctor_to_patient(doc["id"], pat["id"])

patients = get_doctor_patients(doc["id"])
print(patients)