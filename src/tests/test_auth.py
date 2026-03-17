auth_prefix = f"/api/v1/auth"

def test_user_creation(fake_session, fake_user_service, test_client):
    signup_data = {
        "username": "jod35",
        "email": "jodestrevin@gmail.com",
        "first_name": "jonathan",
        "last_name": "ssali",
        "password": "test123",
    }

    response = test_client.post(
        url=f"{auth_prefix}/signup",
        json=signup_data,
    )

    assert fake_user_service.user_exists.called_once()
    assert fake_user_service.user_exists.called_once_with()