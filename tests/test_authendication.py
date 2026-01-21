from app.services.auth_service import authenticate_user

def test_login():
    user = authenticate_user("test_doc_1", "pass123")
    assert user["role"] == "doctor"
