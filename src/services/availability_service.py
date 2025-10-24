from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.db.models import Barber
from src.schemas.availability_schemas import BarberAvailabilityCreate

class BarberAvailabilityService:
    @staticmethod
    def add_or_update_availability(db: Session, barber_id: int, data: BarberAvailabilityCreate):
        """
        Adds or updates barber availability directly in the `barbers` table.
        """
        try:
            # Check if barber exists
            barber = db.query(Barber).filter(Barber.barber_id == barber_id).first()
            if not barber:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Barber with ID {barber_id} not found"
                )

            # Optional: Validate shop ownership
            if hasattr(data, "shop_id") and barber.shop_id != data.shop_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Barber does not belong to this shop"
                )

            # Update barber record directly
            barber.start_time = data.start_time
            barber.end_time = data.end_time
            barber.is_available = data.is_available
            if hasattr(data, "generate_daily"):
                barber.generate_daily = data.generate_daily
            db.commit()
            db.refresh(barber)

            return {
                "msg": "Barber availability updated successfully",
                "barber_id": barber.barber_id
            }

        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e.orig)}"
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error occurred: {str(e)}"
            )
