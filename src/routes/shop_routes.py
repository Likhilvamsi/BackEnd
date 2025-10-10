from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from src.db.database import get_db
from src.services.shop_service import ShopService
from src.schemas.user_schema import ShopResponse,SlotResponse ,BookingRequest
from src.schemas.shop_schemas import ShopCreate
from src.services.shop_service import ShopService

router = APIRouter(prefix="/shops", tags=["Shops"])

router = APIRouter()



# Get all shops
@router.get("/shops/", response_model=List[ShopResponse])
def get_shops(db: Session = Depends(get_db)):
    return ShopService.get_shops_for_user(db, user_id=None)


# Get available slots for a shop
@router.get("/shops/{shop_id}/slots/", response_model=List[SlotResponse])
def get_slots(shop_id: int, date: str = Query(..., description="Date in YYYY-MM-DD format"), db: Session = Depends(get_db)):
    return ShopService.get_available_slots(db, shop_id, date)


@router.get("/owner/{owner_id}")
def get_shops_by_owner(owner_id: int, db: Session = Depends(get_db)):
    """
    Get all shops belonging to a specific owner.
    """
    return ShopService.get_shops_by_owner(db, owner_id)

# Book slots
@router.post("/shops/book-slots/")
def book_slots(request: BookingRequest, db: Session = Depends(get_db)):
    return ShopService.book_slots(
        db, user_id=request.user_id, barber_id=request.barber_id,
        shop_id=request.shop_id, slot_ids=request.slot_ids
    )




@router.post("/create")
def create_shop(
    shop: ShopCreate,
    owner_id: int, 
    db: Session = Depends(get_db)
):
    return ShopService.create_shop_if_not_exists(db, owner_id, shop)
