from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.schemas.barber_schemas import BarberCreate
from src.services.barber_service import BarberService

router = APIRouter(prefix="/barbers", tags=["Barbers"])

@router.post("/add/{shop_id}")
def add_barber(
    shop_id: int,
    barber: BarberCreate,
    db: Session = Depends(get_db)
):
    return BarberService.add_barber(db, shop_id, barber)
@router.delete("/delete/{barber_id}")
def delete_barber(
    barber_id: int,
    owner_id: int,  
    db: Session = Depends(get_db)
):
    return BarberService.delete_barber(db, barber_id, owner_id)
@router.put("/update/{barber_id}")
def update_barber(
    barber_id: int,
    owner_id: int,  # Pass the owner for authorization
    barber_data: BarberCreate,  # You can create a separate Update schema if needed
    db: Session = Depends(get_db)
):
    return BarberService.update_barber(db, barber_id, owner_id, barber_data)


@router.get("/available/{shop_id}")
def get_available_barbers(
    shop_id: int,
    db: Session = Depends(get_db)
):
    return BarberService.get_available_barbers(db, shop_id)
