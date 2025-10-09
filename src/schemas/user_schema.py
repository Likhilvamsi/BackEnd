from pydantic import BaseModel, EmailStr
from typing import Literal,List

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    phone_number: str | None = None
    role: Literal["customer", "owner"] = "customer"  

class OTPRequest(BaseModel):
    email: EmailStr
    role: Literal["customer", "owner"]  

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str
    role: Literal["customer", "owner"]
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
  
# Response models
class ShopResponse(BaseModel):
    shop_id: int
    shop_name: str
    address: str
    city: str
    state: str
    open_time: str
    close_time: str
    is_open: bool

class SlotResponse(BaseModel):
    slot_id: int
    barber_id: int
    barber_name: str
    slot_time: str
    status: str

class BookingRequest(BaseModel):
    user_id: int
    barber_id: int
    shop_id: int
    slot_ids: List[int]