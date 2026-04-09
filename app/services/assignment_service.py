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
# Get All Patients of Doctor
# -----------------------------------------------------

from app.database.connection import get_cursor  # adjust if needed

def get_doctor_patients(doctor_id: int):
    cursor = get_cursor()

    query = """
    SELECT u.id, u.username, u.public_id
    FROM users u
    JOIN doctor_patient_map dpm ON u.id = dpm.patient_id
    WHERE dpm.doctor_id = %s
    AND u.role = 'patient'
    """

    cursor.execute(query, (doctor_id,))
    return cursor.fetchall()

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

