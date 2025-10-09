import smtplib, os
from fastapi import HTTPException
from src.core.logger import logger
from src.core.config import SMTP_EMAIL, SMTP_PASSWORD

def send_email_otp(receiver_email: str, otp: str):
    sender_email = SMTP_EMAIL
    app_password = SMTP_PASSWORD

    subject = "Your OTP Verification Code"
    body = f"Your OTP is {otp}. It will expire in 5 minutes."
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message)
        logger.info(f"[EMAIL OTP] Sent OTP to {receiver_email}")
    except Exception as e:
        logger.error(f"[EMAIL OTP] Failed to send OTP: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP. Try again later.")
