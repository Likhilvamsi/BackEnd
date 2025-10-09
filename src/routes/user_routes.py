# src/routes/user_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.schemas.user_schema import UserCreate, OTPRequest, OTPVerify, UserLogin
from src.services.user_service import UserService

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.register_user(db, user.username, user.email, user.password, user.phone_number, user.role)

@router.post("/send-verification-otp")
def send_verification_otp(request: OTPRequest, db: Session = Depends(get_db)):
    return UserService.send_verification_otp(db, request.email)

@router.post("/verify-email")
def verify_email(request: OTPVerify, db: Session = Depends(get_db)):
    return UserService.verify_email(db, request.email, request.otp)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return UserService.login_with_password(db, user.email, user.password, user.role)


@router.get("/get_user")
def get_user(email: str, db: Session = Depends(get_db)):
    user = UserService.get_user(db, email)
    return user


@router.post("/otp-login")
def send_otp(request: OTPRequest, db: Session = Depends(get_db)):
    return UserService.send_login_otp(db, request.email, request.role)

@router.post("/verify-otp-login")
def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    return UserService.verify_login_otp(db, request.email, request.otp, request.role)
