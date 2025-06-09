import pytest
from models import User
from extensions import db
from app import app as flask_app
from flask_jwt_extended import decode_token


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def create_verified_user(client, email, password):
    """
    Helper function to register and manually verify a user in the database.
    """
    client.post("/signup", json={"email": email, "password": password})
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_verified = True
        db.session.commit()


# ---------- SIGNUP ROUTES TESTS ----------


def test_signup_success(client):
    """
    Test that a valid email and strong password result in successful signup.
    """
    email = "signup_success@gmail.com"
    password = "Test123!"
    res = client.post("/signup", json={"email": email, "password": password})
    assert res.status_code == 200
    assert res.json.get("message") == "User registered"
    assert User.query.filter_by(email=email).first() is not None


def test_signup_missing_credentials(client):
    """
    Test that signup fails if email or password is missing.
    """
    res = client.post("/signup", json={"email": "abc@gmail.com"})  # no password
    assert res.status_code == 400
    assert res.json.get("error") == "Missing credentials"


def test_signup_existing_email(client):
    """
    Test that signing up with an existing email returns 400 and relevant error.
    """
    email = "duplicate@gmail.com"
    password = "Test123!"
    create_verified_user(client, email, password)
    res = client.post("/signup", json={"email": email, "password": password})
    assert res.status_code == 400
    assert res.json.get("error") == "Email already exists"


def test_signup_invalid_email(client):
    """
    Test that an invalid email format returns a 400 error.
    """
    res = client.post("/signup", json={"email": "invalid@", "password": "Test123!"})
    assert res.status_code == 400
    assert res.json.get("error") == "Invalid email"


def test_signup_weak_password(client):
    """
    Test that a weak password returns a 400 error.
    """
    res = client.post("/signup", json={"email": "user@gmail.com", "password": "123"})
    assert res.status_code == 400
    assert res.json.get("error") == "Invalid password"


# ---------- LOGIN ROUTES TESTS ----------


def test_login_success(client):
    """
    Test that a verified user can successfully log in and receive an access token.
    """
    email = "login_success@gmail.com"
    password = "Test123!"
    create_verified_user(client, email, password)
    res = client.post("/logintoken", json={"email": email, "password": password})
    assert res.status_code == 200
    assert "access_token" in res.json


def test_login_missing_credentials(client):
    """
    Test that login fails with missing email or password.
    """
    res = client.post(
        "/logintoken", json={"email": "abc@gmail.com"}
    )  # missing password
    assert res.status_code == 401
    assert res.json.get("error") == "Missing Credentials"


def test_login_wrong_password(client):
    """
    Test that login fails if the password is incorrect.
    """
    email = "wrongpass@gmail.com"
    password = "Test123!"
    create_verified_user(client, email, password)
    res = client.post("/logintoken", json={"email": email, "password": "Wrong123!"})
    assert res.status_code == 401
    assert res.json.get("error") == "Invalid Credentials"


def test_login_unverified_user(client):
    """
    Test that login fails for users who haven't verified their email.
    """
    email = "unverified@gmail.com"
    password = "Test123!"
    client.post(
        "/signup", json={"email": email, "password": password}
    )  # no manual verification
    res = client.post("/logintoken", json={"email": email, "password": password})
    assert res.status_code == 403
    assert res.json.get("error") == "Email not verified"


def test_login_non_existing_user(client):
    """
    Test that login fails if the email is not registered.
    """
    res = client.post(
        "/logintoken", json={"email": "nouser@gmail.com", "password": "Test123!"}
    )
    assert res.status_code == 404
    assert res.json.get("error") == "User not found"


def test_logout_success(client):
    """
    Test that a logged-in user can successfully log out, and the JWT is blacklisted.
    """
    email = "logout_test@gmail.com"
    password = "Test123!"

    create_verified_user(client, email, password)

    res = client.post("/logintoken", json={"email": email, "password": password})
    assert res.status_code == 200
    access_token = res.json.get("access_token")
    assert access_token is not None

    res = client.post("/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    assert res.json.get("message") == "Successfully logged out"

    # Check that the jti was added to the blacklist
    decoded = decode_token(access_token)
    jti = decoded.get("jti")
    assert jti in flask_app.jwt_blacklist


def get_token_and_user_id(client, email, password):
    """Helper to sign up, verify, and return access token + user ID."""
    create_verified_user(client, email, password)
    res = client.post("/logintoken", json={"email": email, "password": password})
    assert res.status_code == 200
    token = res.json.get("access_token")
    user_id = decode_token(token)["sub"]
    return token, user_id


def test_get_profile_success(client):
    """
    Test that an authenticated user can successfully retrieve their profile.
    """
    email = "profile_get@gmail.com"
    password = "Test123!"
    token, _ = get_token_and_user_id(client, email, password)

    res = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json["email"] == email
    assert "id" in res.json
    assert "full_name" in res.json


def test_update_profile_success(client):
    """
    Test that a user can update full_name, phone_number, and address successfully.
    """
    email = "profile_update@gmail.com"
    password = "Test123!"
    token, user_id = get_token_and_user_id(client, email, password)

    update_data = {
        "full_name": "Tamir",
        "phone_number": "0541234567",
        "address": "Herzliya",
    }

    res = client.put(
        "/profile", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json["message"] == "Profile updated successfully"

    # Re-fetch profile to validate update
    res = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.json["full_name"] == "Tamir"
    assert res.json["phone_number"] == "0541234567"
    assert res.json["address"] == "Herzliya"


def create_user_without_verification(client, email, password):
    """Helper to sign up and return the unverified user."""
    client.post("/signup", json={"email": email, "password": password})
    return User.query.filter_by(email=email.lower()).first()


def create_verified_user(client, email, password):
    """Helper to sign up and verify a user."""
    client.post("/signup", json={"email": email, "password": password})
    user = User.query.filter_by(email=email.lower()).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expiry = None
        db.session.commit()


def get_token_and_user_id(client, email, password):
    """Returns access token and user id."""
    create_verified_user(client, email, password)
    res = client.post("/logintoken", json={"email": email, "password": password})
    assert res.status_code == 200
    token = res.json.get("access_token")
    user_id = decode_token(token)["sub"]
    return token, user_id


def test_email_verification_success(client):
    """
    Tests successful email verification via token.
    """
    email = "verify1@example.com"
    password = "Test123!"

    # Register the user
    client.post("/signup", json={"email": email, "password": password})

    # Retrieve user from DB
    user = User.query.filter_by(email=email.lower()).first()
    assert user is not None
    token = user.verification_token
    assert token is not None  # Ensure token exists

    # Call the /verify endpoint
    res = client.get(f"/verify?token={token}")
    assert res.status_code == 200

    # Refresh and validate state
    user = User.query.filter_by(email=email.lower()).first()
    assert user.is_verified is True
    assert user.verification_token is None


def test_email_verification_invalid_token(client):
    """
    Tests that an invalid token returns 404.
    """
    res = client.get("/verify?token=invalidtoken123")
    assert res.status_code == 404
    assert res.json.get("error") == "Invalid token"


def test_email_verification_missing_token(client):
    """
    Tests that missing token returns 400.
    """
    res = client.get("/verify")
    assert res.status_code == 400
    assert res.json.get("error") == "Missing token"


def test_remember_me_extends_token_expiry(client):
    """
    Tests that using 'remember' in login results in a long-expiry token.
    """
    email = "rememberme@example.com"
    password = "Test123!"
    create_verified_user(client, email, password)
    res = client.post(
        "/logintoken", json={"email": email, "password": password, "remember": True}
    )
    assert res.status_code == 200
    token = res.json.get("access_token")
    decoded = decode_token(token)
    assert (decoded["exp"] - decoded["iat"]) > 3600  # More than 1 hour


def test_login_rate_limiting(client):
    """
    Simulates failed login attempts to trigger rate limiting.
    """
    email = "ratelimit@example.com"
    password = "Test123!"
    create_verified_user(client, email, password)
    for _ in range(3):
        client.post("/logintoken", json={"email": email, "password": "Wrong!"})
    res = client.post("/logintoken", json={"email": email, "password": "Wrong!"})
    assert res.status_code == 429
