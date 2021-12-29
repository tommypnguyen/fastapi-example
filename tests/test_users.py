import pytest
from app import schemas, oauth2


def test_create_user(client):
    payload = {"email": "testemail@gmail.com", "password": "password123"}
    res = client.post("/users/", json=payload)
    data = res.json()
    new_user = schemas.UserResponse(**data)
    assert res.status_code == 201
    assert new_user.email == payload["email"]


def test_login_user(client, test_user):
    payload = {"username": test_user["email"], "password": test_user["password"]}
    res = client.post("/login", data=payload)
    new_token = schemas.Token(**res.json())
    token = oauth2.verify_access_token(
        new_token.access_token, credential_exception=oauth2.CREDENTIAL_EXCEPTION
    )
    assert res.status_code == 200
    assert new_token.token_type == "bearer"


@pytest.mark.parametrize(
    "username, password, status_code",
    [
        ("testemail@gmail.com", "wrongpassword", 400),
        ("wrong_email@gmail.com", "password123", 400),
        ("wrong@email.com", "wrongpassword", 400),
        (None, "password123", 422),
        ("testemail@gmail.com", None, 422),
    ],
)
def test_incorrect_login(client, username, password, status_code):
    incorrect_payload = {"username": username, "password": password}
    res = client.post("/login", data=incorrect_payload)
    assert res.status_code == status_code
