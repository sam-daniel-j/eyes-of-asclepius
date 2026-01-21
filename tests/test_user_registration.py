from app.services.user_service import register_user

def test_register_doctor():
    user_id = register_user(
        username="test_doc_1",
        password="pass123",
        role="doctor",
        specialization="Cardiology"
    )
    assert user_id is not None
