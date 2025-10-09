from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.schemas.availability_schemas import BarberAvailabilityCreate
from src.services.availability_service import BarberAvailabilityService

router = APIRouter(prefix="/availability", tags=["Availability"])

@router.post("/add/{barber_id}")
def add_availability(
    barber_id: int,
    data: BarberAvailabilityCreate,
    db: Session = Depends(get_db)
):
    return BarberAvailabilityService.add_or_update_availability(db, barber_id, data)
