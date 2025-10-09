"""from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.core.logger import logger
from src.db.models import Barber, BarberSlot

router = APIRouter()


class SlotResponse(BaseModel):
    slot_id: int
    barber_name: str
    slot_time: str
    status: str


@router.get("/slots/", response_model=list[SlotResponse])
def get_available_slots(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Fetching available slots for date: {date}")
        results = (
            db.query(
                BarberSlot.slot_id,
                Barber.barber_name,
                BarberSlot.slot_time,
                BarberSlot.status
            )
            .join(Barber, BarberSlot.barber_id == Barber.barber_id)
            .filter(BarberSlot.slot_date == date)
            .order_by(Barber.barber_id, BarberSlot.slot_time)
            .all()
        )

        if not results:
            logger.warning(f"No available slots found for {date}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No slots available for {date}"
            )

        fixed_results = [
            {
                "slot_id": row.slot_id,
                "barber_name": row.barber_name,
                "slot_time": str(row.slot_time),
                "status": row.status
            }
            for row in results
        ]

        logger.info(f"Fetched {len(fixed_results)} slots for date {date}")
        return fixed_results

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching slots for {date}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching slots"
        )
"""