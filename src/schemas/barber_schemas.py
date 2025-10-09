from pydantic import BaseModel
from datetime import time

class BarberCreate(BaseModel):
    barber_name: str
    start_time: time
    end_time: time
    
