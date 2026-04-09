-- ================================
-- 🧠 USERS TABLE
-- ================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'doctor', 'patient')),
    specialization VARCHAR(100),
    rsa_public_key TEXT NOT NULL,
    rsa_private_key_encrypted TEXT NOT NULL,
    private_key_salt TEXT,
    public_id VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_public_id ON users(public_id);


-- ================================
-- 🏥 DOCTOR ↔ PATIENT MAPPING
-- ================================
CREATE TABLE IF NOT EXISTS doctor_patient_map (
    id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (doctor_id, patient_id),

    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_doctor_patient_doctor ON doctor_patient_map(doctor_id);
CREATE INDEX IF NOT EXISTS idx_doctor_patient_patient ON doctor_patient_map(patient_id);


-- ================================
-- 📄 MEDICAL RECORDS (ENCRYPTED)
-- ================================
CREATE TABLE IF NOT EXISTS medical_records (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    created_by_doctor_id INT NOT NULL,
    encrypted_data TEXT NOT NULL,
    iv TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_doctor_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_records_patient ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_records_doctor ON medical_records(created_by_doctor_id);


-- ================================
-- 🔐 RECORD KEYS (ACCESS CONTROL)
-- ================================
CREATE TABLE IF NOT EXISTS record_keys (
    id SERIAL PRIMARY KEY,
    record_id INT NOT NULL,
    user_id INT NOT NULL,
    encrypted_aes_key TEXT NOT NULL,
    granted_via VARCHAR(30) NOT NULL CHECK (granted_via IN ('OWNER', 'EMERGENCY', 'REFERRAL')),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (record_id) REFERENCES medical_records(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- ================================
-- 🔁 DOCTOR REFERRALS
-- ================================
CREATE TABLE IF NOT EXISTS doctor_referrals (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    from_doctor_id INT NOT NULL,
    to_doctor_id INT NOT NULL,
    reason TEXT NOT NULL,
    access_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (from_doctor_id) REFERENCES users(id),
    FOREIGN KEY (to_doctor_id) REFERENCES users(id)
);


-- ================================
-- 📜 ACCESS LOGS (AUDIT TRAIL 🔥)
-- ================================
CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    user_id INT,
    patient_id INT,
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
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES users(id)
);


-- ================================
-- 🆔 USER ID GENERATION TRACKER
-- ================================
CREATE TABLE IF NOT EXISTS user_id_counters (
    role VARCHAR(3) NOT NULL,
    year INT NOT NULL,
    last_value INT DEFAULT 0 NOT NULL,

    PRIMARY KEY (role, year)
);