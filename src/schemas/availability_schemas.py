from pydantic import BaseModel
from typing import Optional
from datetime import time, date

class BarberAvailabilityCreate(BaseModel):
    available_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: bool = True
