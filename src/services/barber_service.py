from sqlalchemy.orm import Session
from src.db.models import Barber, Shop
from src.schemas.barber_schemas import BarberCreate
from fastapi import HTTPException

class BarberService:
    @staticmethod
    def add_barber(db: Session, shop_id: int, data: BarberCreate):
        # Check if shop exists
        shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
        if not shop:
            raise HTTPException(status_code=404, detail=f"Shop with id {shop_id} not found")

        # Create barber
        barber = Barber(
            barber_name=data.barber_name,
            shop_id=shop_id,
            start_time=data.start_time,
            end_time=data.end_time,
        )

        db.add(barber)
        db.commit()
        db.refresh(barber)
        return {"msg": "Barber added successfully", "barber_id": barber.barber_id}
