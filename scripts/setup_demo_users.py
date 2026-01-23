from app.services.user_service import register_user

# -------------------------
# ADMINS (2)
# -------------------------
register_user("admin1", "admin123", "admin")
register_user("admin2", "admin123", "admin")

# -------------------------
# DOCTORS (3)
# -------------------------
register_user("dr_smith", "password123", "doctor", "Cardiology")
register_user("dr_jones", "password123", "doctor", "Neurology")
register_user("dr_kumar", "password123", "doctor", "General")

# -------------------------
# PATIENTS (7)
# -------------------------
register_user("anna", "password123", "patient")
register_user("ben", "password123", "patient")
register_user("cara", "password123", "patient")
register_user("dan", "password123", "patient")
register_user("ella", "password123", "patient")
register_user("fred", "password123", "patient")
register_user("gina", "password123", "patient")

print("✅ Demo users created successfully")
