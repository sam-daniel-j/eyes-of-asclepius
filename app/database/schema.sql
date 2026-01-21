-- ==================================================
-- Eyes of Asclepius
-- Secure Hospital Management System
-- Database Schema
-- ==================================================

-- --------------------------
-- USERS TABLE
-- --------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,

    role VARCHAR(20) NOT NULL CHECK (
        role IN ('admin', 'doctor', 'patient')
    ),

    -- Doctor-specific field
    specialization VARCHAR(100),

    -- Cryptographic keys
    rsa_public_key TEXT NOT NULL,
    rsa_private_key_encrypted TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------
-- MEDICAL RECORDS (ENCRYPTED)
-- --------------------------
CREATE TABLE IF NOT EXISTS medical_records (
    id SERIAL PRIMARY KEY,

    patient_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    created_by_doctor_id INTEGER NOT NULL
        REFERENCES users(id),

    encrypted_data TEXT NOT NULL,
    iv TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------
-- RECORD KEYS (HYBRID ENCRYPTION)
-- --------------------------
CREATE TABLE IF NOT EXISTS record_keys (
    id SERIAL PRIMARY KEY,

    record_id INTEGER NOT NULL
        REFERENCES medical_records(id) ON DELETE CASCADE,

    user_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    encrypted_aes_key TEXT NOT NULL,

    granted_via VARCHAR(30) NOT NULL CHECK (
        granted_via IN ('OWNER', 'EMERGENCY', 'REFERRAL')
    ),

    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------
-- DOCTOR REFERRALS
-- --------------------------
CREATE TABLE IF NOT EXISTS doctor_referrals (
    id SERIAL PRIMARY KEY,

    patient_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    from_doctor_id INTEGER NOT NULL
        REFERENCES users(id),

    to_doctor_id INTEGER NOT NULL
        REFERENCES users(id),

    reason TEXT NOT NULL,
    access_expires_at TIMESTAMP NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------
-- ACCESS LOGS (AUDIT TRAIL)
-- --------------------------
CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,

    user_id INTEGER REFERENCES users(id),
    patient_id INTEGER REFERENCES users(id),

    action VARCHAR(40) NOT NULL CHECK (
        action IN (
            'LOGIN',
            'VIEW_RECORD',
            'CREATE_RECORD',
            'EMERGENCY_ACCESS',
            'REFERRAL_GRANTED',
            'REFERRAL_ACCESS',
            'REFERRAL_EXPIRED'
        )
    ),

    justification TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------
-- DOCTOR ↔ PATIENT ASSIGNMENT
-- --------------------------
CREATE TABLE IF NOT EXISTS doctor_patient_map (
    id SERIAL PRIMARY KEY,

    doctor_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    patient_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (doctor_id, patient_id)
);
