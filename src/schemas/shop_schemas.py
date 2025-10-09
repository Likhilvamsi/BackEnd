from pydantic import BaseModel
from datetime import time

class ShopCreate(BaseModel):
    shop_name: str
    address: str
    city: str
    state: str
    open_time: time
    close_time: time
