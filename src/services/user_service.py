from datetime import datetime, timedelta, timezone
import random
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.db.models import User, EmailVerification
from src.repositories.user_repo import UserRepository
from src.core.security import hash_password, verify_password
from src.utils.email import send_email_otp
from src.core.logger import logger

class UserService:

    @staticmethod
    def register_user(db: Session, username: str, email: str, password: str, phone_number: str | None, role: str):
        if UserRepository.get_user_by_email(db, email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if UserRepository.get_user_by_phone(db, phone_number):
            raise HTTPException(status_code=400, detail="phone number already registered")

        hashed_pw = hash_password(password)
        new_user = User(username=username, email=email, hashed_password=hashed_pw, phone_number=phone_number, role=role)
        UserRepository.create_user(db, new_user)

        logger.info(f"[REGISTER] User registered: {email}")
        return {"msg": "User registered successfully"}
    
    @staticmethod
    def get_user(db: Session, email: str):
        user = UserRepository.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number
        }


    @staticmethod
    def send_verification_otp(db: Session, email: str):
        otp = str(random.randint(100000, 999999))
        expiry = datetime.now(timezone.utc) + timedelta(minutes=5)

        record = UserRepository.get_email_verification(db, email)
        if record:
            record.otp_code = otp
            record.otp_expiry = expiry
        else:
            record = EmailVerification(email=email, otp_code=otp, otp_expiry=expiry)

        UserRepository.create_or_update_email_verification(db, record)
        send_email_otp(email, otp)
        return {"msg": "Verification OTP sent"}

    @staticmethod
    def verify_email(db: Session, email: str, otp: str):
        record = UserRepository.get_email_verification(db, email)
        if not record:
            raise HTTPException(status_code=404, detail="Email not found")
        if record.otp_code != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        if datetime.now(timezone.utc) > record.otp_expiry.replace(tzinfo=timezone.utc):
            UserRepository.delete_email_verification(db, record)
            raise HTTPException(status_code=400, detail="OTP expired")

        UserRepository.delete_email_verification(db, record)
        return {"msg": "Email verified successfully"}

    @staticmethod
    def login_with_password(db: Session, email: str, password: str, role: str):
        user = UserRepository.get_user_by_email(db, email)
        if not user or user.role != role:
            raise HTTPException(status_code=401, detail="Invalid email or role")
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        logger.info(f"[LOGIN] Success: {email}")
        return {
            "msg": "Login successful",
            "user_id": user.id,
            "role": user.role
        }


    @staticmethod
    def send_login_otp(db: Session, email: str, role: str):
        user = UserRepository.get_user_by_email(db, email)
        if not user or user.role != role:
            raise HTTPException(status_code=401, detail="Invalid email or role")

        otp = str(random.randint(100000, 999999))
        expiry = datetime.now(timezone.utc) + timedelta(minutes=5)

        user.otp_code = otp
        user.otp_expiry = expiry
        user.otp_channel = "email"

        UserRepository.update_user(db, user)
        send_email_otp(user.email, otp)

        return {"msg": f"OTP sent successfully for {role}"}


    @staticmethod
    def verify_login_otp(db: Session, email: str, otp: str, role: str):
        user = UserRepository.get_user_by_email(db, email)
        if not user or user.role != role:
            raise HTTPException(status_code=401, detail="Invalid email or role")
        if user.otp_code != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        if datetime.now(timezone.utc) > user.otp_expiry.replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=400, detail="OTP expired")

        user.otp_code, user.otp_expiry = None, None
        UserRepository.update_user(db, user)

        logger.info(f"[OTP LOGIN] Success: {email} ({role})")
        return {
            "msg": f"Login successful as {role}",
            "user_id": user.id,
            "role": user.role
        }


