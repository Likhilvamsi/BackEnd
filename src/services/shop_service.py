from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from src.db.models import Shop, Barber, BarberSlot, Booking
from src.core.logger import logger
from sqlalchemy.orm import Session
from src.schemas.shop_schemas import ShopCreate


class ShopService:

    @staticmethod
    def get_shops_for_user(db: Session, user_id: int):
        """
        Fetch shops owned by a user or all shops (if user is customer)
        """
        shops = db.query(Shop).all()
        if not shops:
            raise HTTPException(status_code=404, detail="No shops found")

        return [
            {
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "address": shop.address,
                "city": shop.city,
                "state": shop.state,
                "open_time": str(shop.open_time),
                "close_time": str(shop.close_time),
                "is_open": shop.is_open
            } for shop in shops
        ]

    @staticmethod
    def get_available_slots(db: Session, shop_id: int, date: str):
        results = (
            db.query(
                BarberSlot.slot_id,
                Barber.barber_id,        # include barber_id
                Barber.barber_name,
                BarberSlot.slot_time,
                BarberSlot.status
            )
            .join(Barber, BarberSlot.barber_id == Barber.barber_id)
            .filter(BarberSlot.shop_id == shop_id, BarberSlot.slot_date == date)
            .order_by(Barber.barber_id, BarberSlot.slot_time)
            .all()
        )

        if not results:
            raise HTTPException(status_code=404, detail="No available slots for this shop on the selected date")

        # Build list including barber_id
        return [
            {
                "slot_id": row.slot_id,
                "barber_id": row.barber_id,       # <-- important
                "barber_name": row.barber_name,
                "slot_time": str(row.slot_time),
                "status": row.status
            }
            for row in results
        ]

        
    @staticmethod
    def create_shop_if_not_exists(db, owner_id, shop_data):
        from src.db.models import Shop, User
        from fastapi import HTTPException
        
        user = db.query(User).filter(User.id == owner_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Owner not found")
 
        if user.role not in ["owner", "shop_owner"]:
            raise HTTPException(status_code=403, detail="User is not authorized to create a shop")
    
        existing_shop = db.query(Shop).filter(Shop.owner_id == owner_id).first()
        if existing_shop:
            return {"message": "Shop already exists", "shop_id": existing_shop.shop_id}

        new_shop = Shop(
            owner_id=owner_id,
            shop_name=shop_data.shop_name,
            address=shop_data.address,
            city=shop_data.city,
            state=shop_data.state,
            open_time=shop_data.open_time,
            close_time=shop_data.close_time,
        )

        db.add(new_shop)
        db.commit()
        db.refresh(new_shop)

        return {"message": "Shop created successfully", "shop_id": new_shop.shop_id}


              
    @staticmethod
    def book_slots(db: Session, user_id: int, barber_id: int, shop_id: int, slot_ids: list[int]):
        booked_slots = []

        for slot_id in slot_ids:
            slot = db.query(BarberSlot).filter(BarberSlot.slot_id == slot_id, BarberSlot.shop_id == shop_id).first()
            if not slot:
                raise HTTPException(status_code=404, detail=f"Slot {slot_id} not found")
            if slot.is_booked:
                raise HTTPException(status_code=400, detail=f"Slot {slot_id} already booked")

            # mark slot booked
            slot.is_booked = True
            slot.status = "booked"

            # create booking record
            booking = Booking(
                user_id=user_id,
                barber_id=barber_id,
                shop_id=shop_id,
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
            "user_id": user_id,
            "barber_id": barber_id,
            "shop_id": shop_id,
            "booked_slots": booked_slots
        }
    

    @staticmethod
    def get_shops_by_owner(db: Session, owner_id: int):
        """
        Fetch all shops belonging to a specific owner.
        """
        from src.db.models import Shop

        shops = db.query(Shop).filter(Shop.owner_id == owner_id).all()

        if not shops:
            raise HTTPException(status_code=404, detail=f"No shops found for owner_id {owner_id}")

        return [
            {
                "shop_id": shop.shop_id,
                "shop_name": shop.shop_name,
                "address": shop.address,
                "city": shop.city,
                "state": shop.state,
                "open_time": str(shop.open_time),
                "close_time": str(shop.close_time),
                "is_open": shop.is_open,
            }
            for shop in shops
        ]


