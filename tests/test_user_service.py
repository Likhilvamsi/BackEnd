import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from unittest.mock import patch
from src.db.test_database import init_test_db, TestingSessionLocal
from src.services.user_service import UserService
from src.db.models import User, EmailVerification
from src.repositories.user_repo import UserRepository
from src.core.security import hash_password

@pytest.fixture(scope="module")
def test_db():
    init_test_db()
    db = TestingSessionLocal()
    yield db
    db.close()


def test_register_user_success(test_db: Session):
    user_data = {
        "username": "john",
        "email": "john@example.com",
        "password": "password123",
        "phone_number": "9999999999",
        "role": "customer"
    }

    result = UserService.register_user(
        db=test_db,
        username=user_data["username"],
        email=user_data["email"],
        password=user_data["password"],
        phone_number=user_data["phone_number"],
        role=user_data["role"]
    )

    assert result["msg"] == "User registered successfully"
    saved_user = test_db.query(User).filter(User.email == user_data["email"]).first()
    assert saved_user is not None


def test_register_user_existing_email(test_db: Session):
    with pytest.raises(HTTPException) as exc_info:
        UserService.register_user(
            db=test_db,
            username="another",
            email="john@example.com",  # already used
            password="test",
            phone_number="8888888888",
            role="customer"
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"


def test_get_user_success(test_db: Session):
    result = UserService.get_user(test_db, email="john@example.com")
    assert result["username"] == "john"
    assert result["email"] == "john@example.com"


def test_get_user_not_found(test_db: Session):
    with pytest.raises(HTTPException) as exc_info:
        UserService.get_user(test_db, email="notfound@example.com")
    assert exc_info.value.status_code == 404


@patch("src.services.user_service.send_email_otp")
def test_send_verification_otp(mock_send_email, test_db: Session):
    mock_send_email.return_value = True
    result = UserService.send_verification_otp(test_db, "john@example.com")
    assert result["msg"] == "Verification OTP sent"
    record = test_db.query(EmailVerification).filter_by(email="john@example.com").first()
    assert record is not None


def test_verify_email_success(test_db: Session):
    # Get OTP record and verify it
    record = test_db.query(EmailVerification).filter_by(email="john@example.com").first()
    otp = record.otp_code
    result = UserService.verify_email(test_db, "john@example.com", otp)
    assert result["msg"] == "Email verified successfully"


def test_login_with_password_success(test_db: Session):
    # Create user manually for login test
    hashed_pw = hash_password("mypassword")
    user = User(username="loginuser", email="login@example.com",
                hashed_password=hashed_pw, phone_number="7777777777", role="customer")
    test_db.add(user)
    test_db.commit()

    result = UserService.login_with_password(test_db, "login@example.com", "mypassword", "customer")
    assert result["msg"] == "Login successful"
    assert result["role"] == "customer"


def test_login_with_invalid_password(test_db: Session):
    with pytest.raises(HTTPException) as exc_info:
        UserService.login_with_password(test_db, "login@example.com", "wrongpass", "customer")
    assert exc_info.value.status_code == 401
