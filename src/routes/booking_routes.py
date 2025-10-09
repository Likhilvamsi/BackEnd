from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.services.booking_service import BookingService
from typing import List

router = APIRouter()


class BookingRequest(BaseModel):
    user_id: int
    barber_id: int
    shop_id: int
    slot_ids: List[int]  # multiple slots


@router.post("/book-slots/")
def book_slots(request: BookingRequest, db: Session = Depends(get_db)):
    try:
        booked_slots = BookingService.book_slots(
            db=db,
            user_id=request.user_id,
            barber_id=request.barber_id,
            shop_id=request.shop_id,
            slot_ids=request.slot_ids
        )
        return {
            "message": f"{len(booked_slots)} slots booked successfully",
            "user_id": request.user_id,
            "barber_id": request.barber_id,
            "shop_id": request.shop_id,
            "booked_slots": booked_slots
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
