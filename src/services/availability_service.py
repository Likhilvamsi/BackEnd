from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.db.models import Barber, BarberAvailability
from src.schemas.availability_schemas import BarberAvailabilityCreate

class BarberAvailabilityService:
    @staticmethod
    def add_or_update_availability(db: Session, barber_id: int, data: BarberAvailabilityCreate):
        """
        Adds or updates barber availability after validating the barber.
        """
        try:
            # Check if barber exists
            barber = db.query(Barber).filter(Barber.barber_id == barber_id).first()
            if not barber:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Barber with ID {barber_id} not found"
                )

            #  Validate shop ownership (optional)
            if hasattr(data, "shop_id") and barber.shop_id != data.shop_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Barber does not belong to this shop"
                )

            #  Check if availability already exists
            record = db.query(BarberAvailability).filter(
                BarberAvailability.barber_id == barber_id,
                BarberAvailability.available_date == data.available_date
            ).first()

            if record:
                record.start_time = data.start_time
                record.end_time = data.end_time
                record.is_available = data.is_available
                db.commit()
                db.refresh(record)
                return {
                    "msg": "Availability updated successfully",
                    "availability_id": record.id
                }

            #  Create new record
            new_record = BarberAvailability(
                barber_id=barber_id,
                available_date=data.available_date,
                start_time=data.start_time,
                end_time=data.end_time,
                is_available=data.is_available
            )
            db.add(new_record)
            db.commit()
            db.refresh(new_record)

            return {
                "msg": "Availability added successfully",
                "availability_id": new_record.id
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
