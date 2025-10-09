from sqlalchemy import Column,UniqueConstraint, Integer, String, DateTime, Date, Time, Boolean, Text, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.database import Base
from datetime import datetime, timedelta, time, date
import enum

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    role = Column(String(20), default="customer")  # customer / shop_owner
    otp_code = Column(String(10), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Shop(Base):
    __tablename__ = "shops"
    
    shop_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shop_name = Column(String(200), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User")
    barbers = relationship("Barber", back_populates="shop", cascade="all, delete")


class Barber(Base):
        __tablename__ = "barbers"
        
        barber_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        barber_name = Column(String(200), nullable=False)
        shop_id = Column(Integer, ForeignKey("shops.shop_id"), nullable=False)
        start_time = Column(Time, nullable=False)
        end_time = Column(Time, nullable=False)
        is_available = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        
        shop = relationship("Shop", back_populates="barbers")
        slots = relationship("BarberSlot", back_populates="barber", cascade="all, delete")

    
        availability = relationship(
        "BarberAvailability",
        back_populates="barber",
        cascade="all, delete"
    )


class BarberSlot(Base):
    __tablename__ = "barber_slots"

    slot_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    barber_id = Column(Integer, ForeignKey("barbers.barber_id"), nullable=False)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), nullable=False)  # ✅ ADD THIS
    slot_date = Column(Date, nullable=False)
    slot_time = Column(Time, nullable=False)
    is_booked = Column(Boolean, default=False)
    status = Column(String(20), default="available")
    created_at = Column(DateTime, default=datetime.utcnow)

    barber = relationship("Barber", back_populates="slots")


class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    barber_id = Column(Integer, ForeignKey("barbers.barber_id"), nullable=False)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("barber_slots.slot_id"), nullable=False)
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    status = Column(String(20), default="booked")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    barber = relationship("Barber")
    shop = relationship("Shop")
    slot = relationship("BarberSlot")

from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, Time, Date, DateTime, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from src.db.database import Base




class EmailVerification(Base):
    __tablename__ = "email_verification"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False)
    otp_code = Column(String(10), nullable=False)
    otp_expiry = Column(DateTime, nullable=False)
    
class BarberAvailability(Base):
    __tablename__ = "barber_availability"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    barber_id = Column(Integer, ForeignKey("barbers.barber_id"), nullable=False)
    available_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    barber = relationship("Barber", back_populates="availability")

    __table_args__ = (
        UniqueConstraint("barber_id", "available_date", name="uq_barber_availability"),
    )
