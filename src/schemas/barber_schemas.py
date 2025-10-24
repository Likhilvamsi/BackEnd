from pydantic import BaseModel
from typing import Optional
from datetime import time

class BarberCreate(BaseModel):
    barber_name: str
    start_time: time
    end_time: time
    is_available: bool = True
    everyday: bool = False  # ✅ Checkbox flag

class BarberUpdate(BaseModel):
    barber_name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None
    everyday: Optional[bool] = None  # ✅ Allow updating recurring availability
