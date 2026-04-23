from typing import Optional, Dict, Any
from app.database.connection import get_cursor, commit


# ==============================
# CREATE MEDICAL RECORD
# ==============================
def create_medical_record(patient_id, doctor_id, encrypted_data, iv):
    cur = get_cursor()

    cur.execute("""
        INSERT INTO medical_records
        (patient_id, created_by_doctor_id, encrypted_data, iv)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (patient_id, doctor_id, encrypted_data, iv))

    row = cur.fetchone()

    if not row:
        raise Exception("Insert failed - no ID returned")

    commit()

    # 🔥 handle both tuple + dict cursor
    if isinstance(row, dict):
        return row["id"]
    else:
        return row[0]


# ==============================
# STORE RECORD KEY
# ==============================
def store_record_key(record_id, user_id, encrypted_aes_key, granted_via):
    cur = get_cursor()

    cur.execute("""
        INSERT INTO record_keys
        (record_id, user_id, encrypted_aes_key, granted_via)
        VALUES (%s, %s, %s, %s)
    """, (record_id, user_id, encrypted_aes_key, granted_via))

    commit()


# ==============================
# GET RECORD WITH ACCESS KEY
# ==============================
def get_record_with_key(record_id, user_id):
    cur = get_cursor()

    cur.execute("""
        SELECT
            mr.id,
            mr.patient_id,
            mr.encrypted_data,
            mr.iv,
            rk.encrypted_aes_key
        FROM medical_records mr
        JOIN record_keys rk ON rk.record_id = mr.id
        WHERE mr.id = %s
          AND rk.user_id = %s
          AND (rk.expires_at IS NULL OR rk.expires_at > NOW())
    """, (record_id, user_id))

    return cur.fetchone()


# ==============================
# GET ALL RECORDS FOR PATIENT
# ==============================
def get_patient_records(patient_id):
    cur = get_cursor()

    cur.execute("""
        SELECT id, created_at
        FROM medical_records
        WHERE patient_id = %s
        ORDER BY created_at DESC
    """, (patient_id,))

    return cur.fetchall()


# ==============================
# GET LATEST RECORD
# ==============================
def get_latest_record(patient_id):
    cur = get_cursor()

    cur.execute("""
        SELECT id
        FROM medical_records
        WHERE patient_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (patient_id,))

    return cur.fetchone()


# ==============================
# GET PRIMARY DOCTORS
# ==============================
def get_patient_doctors(patient_id):
    cur = get_cursor()

    cur.execute("""
        SELECT DISTINCT u.username, u.specialization
        FROM medical_records mr
        JOIN users u ON u.id = mr.created_by_doctor_id
        WHERE mr.patient_id = %s
    """, (patient_id,))

    return cur.fetchall()


# ==============================
# GET REFERRAL DOCTORS
# ==============================
def get_referral_doctors(patient_id):
    cur = get_cursor()

    cur.execute("""
        SELECT u.username, u.specialization
        FROM doctor_referrals dr
        JOIN users u ON u.id = dr.to_doctor_id
        WHERE dr.patient_id = %s
          AND dr.is_active = TRUE
    """, (patient_id,))

    return cur.fetchall()