# src/repositories/user_repository.py
from sqlalchemy.orm import Session
from src.db.models import User, EmailVerification

class UserRepository:

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()
    # in user_repo.py
    @staticmethod
    def get_user_by_phone(db: Session, phone_number: str):
        return db.query(User).filter(User.phone_number == phone_number).first()


    @staticmethod
    def create_user(db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_email_verification(db: Session, email: str):
        return db.query(EmailVerification).filter(EmailVerification.email == email).first()

    @staticmethod
    def create_or_update_email_verification(db: Session, record: EmailVerification):
        db.add(record)
        db.commit()
        return record

    @staticmethod
    def delete_email_verification(db: Session, record: EmailVerification):
        db.delete(record)
        db.commit()

    @staticmethod
    def update_user(db: Session, user: User):
        db.add(user)
        db.commit()
        return user
