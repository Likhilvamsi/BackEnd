"""from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import BarberSlot, Booking
from typing import List

router = APIRouter()

class BookingRequest(BaseModel):
    user_id: int
    barber_id: int
    shop_id: int
    slot_ids: List[int]   # multiple slots

@router.post("/book-slots/")
def book_slots(request: BookingRequest, db: Session = Depends(get_db)):
    booked_slots = []

    for slot_id in request.slot_ids:
        # 1. Fetch slot
        slot = db.query(BarberSlot).filter(BarberSlot.slot_id == slot_id).first()
        if not slot:
            raise HTTPException(status_code=404, detail=f"Slot {slot_id} not found")

        if slot.is_booked:
            raise HTTPException(status_code=400, detail=f"Slot {slot_id} already booked")

        # 2. Mark slot as booked
        slot.is_booked = True
        slot.status = "booked"

        # 3. Create booking record
        booking = Booking(
            user_id=request.user_id,
            barber_id=request.barber_id,
            shop_id=request.shop_id,
            slot_id=slot.slot_id,
            booking_date=slot.slot_date,
            booking_time=slot.slot_time,
            status="booked",
        )

        db.add(booking)
        booked_slots.append({
            "slot_id": slot.slot_id,
            "slot_date": str(slot.slot_date),
            "slot_time": str(slot.slot_time),
            "status": booking.status
        })

    db.commit()

    return {
        "message": f"{len(booked_slots)} slots booked successfully",
        "user_id": request.user_id,
        "barber_id": request.barber_id,
        "shop_id": request.shop_id,
        "booked_slots": booked_slots
    }

"""