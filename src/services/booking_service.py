from sqlalchemy.orm import Session
from datetime import datetime
from src.db.models import BarberSlot, Booking

class BookingService:
    @staticmethod
    def book_slots(db: Session, user_id: int, barber_id: int, shop_id: int, slot_ids: list):
        booked_slots = []

        for slot_id in slot_ids:
            # Fetch slot
            slot = db.query(BarberSlot).filter(
                BarberSlot.slot_id == slot_id,
                BarberSlot.barber_id == barber_id
            ).first()

            if not slot:
                raise ValueError(f"Slot {slot_id} not found")

            if slot.is_booked:
                raise ValueError(f"Slot {slot_id} is already booked")

            # Mark slot as booked
            slot.is_booked = True
            slot.status = "booked"

            # Create booking record
            booking = Booking(
                user_id=user_id,
                barber_id=barber_id,
                shop_id=shop_id,
                slot_id=slot.slot_id,
                booking_date=slot.slot_date,
                booking_time=slot.slot_time,
                status="booked",
                created_at=datetime.utcnow()
            )

            db.add(booking)
            booked_slots.append({
                "slot_id": slot.slot_id,
                "slot_date": str(slot.slot_date),
                "slot_time": str(slot.slot_time),
                "status": booking.status
            })

        db.commit()
        return booked_slots
