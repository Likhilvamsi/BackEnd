from sqlalchemy.orm import Session
from src.db.models import Barber, Shop
from src.schemas.barber_schemas import BarberCreate, BarberUpdate
from fastapi import HTTPException

class BarberService:
    
    @staticmethod
    def add_barber(db: Session, shop_id: int, data: BarberCreate):
        shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
        if not shop:
            raise HTTPException(status_code=404, detail=f"Shop with id {shop_id} not found")

        barber = Barber(
            barber_name=data.barber_name,
            shop_id=shop_id,
            start_time=data.start_time,
            end_time=data.end_time,
            is_available=data.is_available,
            generate_daily=data.everyday  # ✅ Set daily slot generation
        )

        db.add(barber)
        db.commit()
        db.refresh(barber)
        return {"msg": "Barber added successfully", "barber_id": barber.barber_id}

    @staticmethod
    def update_barber(db: Session, barber_id: int, owner_id: int, data: BarberUpdate):
        barber = db.query(Barber).filter(Barber.barber_id == barber_id).first()
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")

        shop = db.query(Shop).filter(Shop.shop_id == barber.shop_id).first()
        if shop.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this barber")

        barber.barber_name = data.barber_name or barber.barber_name
        barber.start_time = data.start_time or barber.start_time
        barber.end_time = data.end_time or barber.end_time
        barber.is_available = data.is_available if data.is_available is not None else barber.is_available
        barber.generate_daily = data.everyday if data.everyday is not None else barber.generate_daily  # ✅ Update daily

        db.commit()
        db.refresh(barber)
        return {"msg": "Barber updated successfully", "barber": {
            "barber_id": barber.barber_id,
            "name": barber.barber_name,
            "start_time": str(barber.start_time),
            "end_time": str(barber.end_time),
            "is_available": barber.is_available,
            "everyday": barber.generate_daily  # ✅ Return daily info
        }}


    @staticmethod
    def delete_barber(db: Session, barber_id: int, owner_id: int):
        barber = db.query(Barber).filter(Barber.barber_id == barber_id).first()
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")

        # Ensure only the owner of the shop can delete the barber
        shop = db.query(Shop).filter(Shop.shop_id == barber.shop_id).first()
        if shop.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this barber")

        db.delete(barber)  # ✅ No need to delete related slots/bookings manually
        db.commit()

        return {"msg": "Barber and all related records deleted successfully"}
    

    @staticmethod
    def get_available_barbers(db: Session, shop_id: int):
        barbers = db.query(Barber).filter(
            Barber.shop_id == shop_id,
            Barber.is_available == True
        ).all()

        if not barbers:
            raise HTTPException(status_code=404, detail="No available barbers found for this shop")

        return [
            {
                "barber_id": barber.barber_id,
                "name": barber.barber_name,
                "start_time": str(barber.start_time),
                "end_time": str(barber.end_time),
                "is_available": barber.is_available
            }
            for barber in barbers
        ]

