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
