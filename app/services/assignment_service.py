from app.database.connection import get_cursor, commit


# -----------------------------------------------------
# Assign Doctor to Patient
# -----------------------------------------------------

def assign_doctor_to_patient(doctor_id: int, patient_id: int):
    cur = get_cursor()

    cur.execute(
        """
        INSERT INTO doctor_patient_map (doctor_id, patient_id)
        VALUES (%s, %s)
        ON CONFLICT (doctor_id, patient_id) DO NOTHING;
        """,
        (doctor_id, patient_id)
    )

    commit()


# -----------------------------------------------------
# Check If Doctor Is Assigned
# -----------------------------------------------------

def is_doctor_assigned(doctor_id: int, patient_id: int) -> bool:
    cur = get_cursor()

    cur.execute(
        """
        SELECT 1
        FROM doctor_patient_map
        WHERE doctor_id = %s AND patient_id = %s;
        """,
        (doctor_id, patient_id)
    )

    return cur.fetchone() is not None


# -----------------------------------------------------
# Get Assigned Patients
# -----------------------------------------------------

def get_doctor_patients(doctor_id: int):
    cur = get_cursor()

    cur.execute(
        """
        SELECT u.id, u.username, u.public_id
        FROM users u
        JOIN doctor_patient_map dpm ON u.id = dpm.patient_id
        WHERE dpm.doctor_id = %s
        AND u.role = 'patient'
        """,
        (doctor_id,)
    )

    return cur.fetchall()


# -----------------------------------------------------
# 🔁 Get Referred Patients (NEW)
# -----------------------------------------------------

def get_referred_patients(doctor_id: int):
    cur = get_cursor()

    cur.execute(
        """
        SELECT DISTINCT u.id, u.username, u.public_id
        FROM doctor_referrals r
        JOIN users u ON u.id = r.patient_id
        WHERE r.to_doctor_id = %s
        AND r.is_active = TRUE
        """,
        (doctor_id,)
    )

    return cur.fetchall()


# -----------------------------------------------------
# 🧠 Get ALL Patients (Assigned + Referred)
# -----------------------------------------------------

def get_all_patients_for_doctor(doctor_id: int):
    assigned = get_doctor_patients(doctor_id)
    referred = get_referred_patients(doctor_id)

    patient_map = {}

    # Assigned first (priority)
    for p in assigned:
        patient_map[p["id"]] = {
            **p,
            "type": "Assigned 🟢"
        }

    # Add referred if not already present
    for p in referred:
        if p["id"] not in patient_map:
            patient_map[p["id"]] = {
                **p,
                "type": "Referred 🔁"
            }

    return list(patient_map.values())


# -----------------------------------------------------
# Get All Doctors of Patient
# -----------------------------------------------------

def get_patient_doctors(patient_id: int):
    cur = get_cursor()

    cur.execute(
        """
        SELECT u.id, u.public_id, u.username
        FROM doctor_patient_map dpm
        JOIN users u ON u.id = dpm.doctor_id
        WHERE dpm.patient_id = %s
        ORDER BY u.id;
        """,
        (patient_id,)
    )

    return cur.fetchall()