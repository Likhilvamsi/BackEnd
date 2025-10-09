from datetime import datetime, timedelta
from src.db.database import SessionLocal
from src.db.models import Barber, BarberAvailability, BarberSlot
from src.core.logger import logger

def generate_barber_slots():
    """Generate 1-hour slots for barbers based on their availability."""
    db = SessionLocal()
    try:
        today = datetime.today().date()
        current_time = datetime.now().time()  # current time
        slot_duration = timedelta(hours=1)

        # Get all barbers with availability for today
        availabilities = db.query(BarberAvailability).filter(
            BarberAvailability.available_date >= today,
            BarberAvailability.is_available == True
        ).all()

        if not availabilities:
            logger.info("[SLOT AGENT] No availabilities found for today")
            return

        for availability in availabilities:
            barber = db.query(Barber).filter(
                Barber.barber_id == availability.barber_id
            ).first()

            if not barber:
                logger.warning(f"[SLOT AGENT] Barber ID {availability.barber_id} not found, skipping")
                continue

            if not availability.start_time or not availability.end_time:
                logger.warning(f"[SLOT AGENT] Barber {barber.barber_name} missing start/end time, skipping")
                continue

            # Combine date with times
            start_dt = datetime.combine(today, availability.start_time)
            end_dt = datetime.combine(today, availability.end_time)

            # Only create slots for times in the future
            now_dt = datetime.now()
            if end_dt <= now_dt:
                logger.info(f"[SLOT AGENT] Barber {barber.barber_name} availability has already ended")
                continue

            # Start from now or the availability start time (whichever is later)
            current_slot_start = max(start_dt, now_dt)

            while current_slot_start + slot_duration <= end_dt:
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
    shop_id=barber.shop_id,   # ✅ Add this line
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
