# 🧠 Eyes of Asclepius

### 🔐 Real-Time Encryption for Hospital Management System

---

## 📌 Overview

**Eyes of Asclepius** is a secure hospital management system designed to protect sensitive medical data using **end-to-end encryption**.

The system ensures that:

* Medical records are **encrypted before storage**
* Only **authorized users** can decrypt and access data
* All access is **tracked and logged**

---

## 🔗 GitHub Repository

👉 https://github.com/sam-daniel-j/eyes-of-asclepius.git

---

## 🚀 Key Features

### 🔐 Core Security

* AES-256 encryption for medical records
* RSA-based hybrid encryption for secure key sharing
* Encryption before database storage (zero plaintext policy)

### 👨‍⚕️ Role-Based Access Control

* **Doctor**:

  * View assigned patients
  * Add and edit medical records
* **Patient**:

  * View own records only
* **Admin**:

  * Requires permission before accessing records

### 🧾 Access Logging

* Every access is recorded in `access_logs`

### 🆔 Custom ID System

* `PAT-2026-001`, `DOC-2026-001`, `ADM-2026-001`

---

## 🏗️ System Architecture

```text
Frontend (Streamlit)
        ↓
Service Layer (Business Logic)
        ↓
Security Layer (AES + RSA Hybrid)
        ↓
Database (PostgreSQL)
```

---

## 📂 Project Structure

```text
eyes-of-asclepius/
│
├── app/
│   ├── main.py
│   ├── ui/
│   ├── services/
│   ├── models/
│   ├── security/
│   ├── database/
│   └── utils/
│
├── schema.sql
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/sam-daniel-j/eyes-of-asclepius.git
cd eyes-of-asclepius
```

---

### 2️⃣ Create Virtual Environment (venv)

#### ▶️ Windows

```bash
python -m venv .eyes
.eyes\Scripts\activate
```

#### ▶️ Linux / Mac

```bash
python3 -m venv .eyes
source .eyes/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup PostgreSQL

Create database:

```sql
CREATE DATABASE eyes_of_asclepius;
```

Run schema:

```bash
psql -U postgres -d eyes_of_asclepius -f schema.sql
```

---

### 5️⃣ Configure Database

Update credentials in:

```
app/database/connection.py
```

---

### 6️⃣ Run Application

```bash
streamlit run app/main.py
```

---

## 🧪 Testing

### Doctor

* View assigned patients
* Add medical records

### Patient

* View latest record
* View history

### Admin

* Manage access

---

## ⚠️ Notes

* Old records created before encryption fixes may not decrypt
* Always test using newly created records

---

## 🔮 Future Enhancements

* 🚨 Emergency access with controlled key sharing
* 🔐 OTP-based temporary access
* 📊 AI-based anomaly detection
* 📱 Mobile application

---

## 👨‍💻 Tech Stack

* Python
* Streamlit
* PostgreSQL
* AES + RSA Hybrid Encryption

---

## 🏁 Status

✅ Fully Functional
🚀 Ready for Demo / Submission

---
