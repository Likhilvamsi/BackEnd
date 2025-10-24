from datetime import datetime, timedelta
from src.db.database import SessionLocal
from src.db.models import Barber, BarberSlot, Shop
from src.core.logger import logger

def generate_barber_slots(single_barber_id: int = None):
    """Generate 1-hour slots for barbers directly from barbers table with fixed time intervals."""
    db = SessionLocal()
    try:
        today = datetime.today().date()
        now_dt = datetime.now()
        slot_duration = timedelta(hours=1)

        # Fetch barbers eligible for daily slot generation
        query = db.query(Barber).filter(
            Barber.generate_daily == True,
            Barber.is_available == True
        )
        if single_barber_id:
            query = query.filter(Barber.barber_id == single_barber_id)

        barbers = query.all()

        if not barbers:
            logger.info("[SLOT AGENT] No barbers found for slot generation")
            return

        for barber in barbers:
            # Ensure shop is open
            shop = db.query(Shop).filter(Shop.shop_id == barber.shop_id).first()
            if not shop or not getattr(shop, "is_open", True):
                logger.info(f"[SLOT AGENT] Shop closed. Skipping {barber.barber_name}.")
                continue

            # Validate barber start/end times
            if not barber.start_time or not barber.end_time:
                logger.warning(f"[SLOT AGENT] Barber {barber.barber_name} missing start/end time, skipping")
                continue

            start_dt = datetime.combine(today, barber.start_time)
            end_dt = datetime.combine(today, barber.end_time)

            # Start from barber's start_time and generate fixed 1-hour slots
            current_slot_start = start_dt

            while current_slot_start + slot_duration <= end_dt:
                # Skip past slots
                if current_slot_start + slot_duration <= now_dt:
                    current_slot_start += slot_duration
                    continue

                slot_time = current_slot_start.time()

                # Check if slot already exists
                exists = db.query(BarberSlot).filter(
                    BarberSlot.barber_id == barber.barber_id,
                    BarberSlot.slot_date == today,
                    BarberSlot.slot_time == slot_time
                ).first()

                if not exists:
                    new_slot = BarberSlot(
                        barber_id=barber.barber_id,
                        shop_id=barber.shop_id,
                        slot_date=today,
                        slot_time=slot_time,
                        status="available",
                        is_booked=False
                    )
                    db.add(new_slot)
                    logger.info(f"[SLOT AGENT] Created slot for {barber.barber_name} at {slot_time}")

                current_slot_start += slot_duration

        db.commit()
        logger.info("[SLOT AGENT] Slots generation completed successfully")

    except Exception as e:
        db.rollback()
        logger.error(f"[SLOT AGENT ERROR] {str(e)}")
    finally:
        db.close()
