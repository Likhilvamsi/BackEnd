# app/routers/phones.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db.database import async_engine as engine 
from core.logger import logger   

router = APIRouter()

class PhoneNumberRequest(BaseModel):
    emp_id: int
    phone_number: constr(pattern=r"^\d{10}$")  # Must be exactly 10 digits


@router.post("/")
async def add_phone_number(data: PhoneNumberRequest):
    try:
        async with engine.connect() as connection:
            # Check if the employee exists
            emp_exists = await connection.execute(
                text("SELECT 1 FROM employee_details WHERE emp_id = :emp_id"),
                {"emp_id": data.emp_id}
            )

            if not emp_exists.fetchone():
                logger.warning(f"Tried adding phone for non-existent emp_id={data.emp_id}")
                raise HTTPException(status_code=404, detail="Employee ID does not exist.")

            # Check if the phone number already exists for this employee
            duplicate_exists = await connection.execute(
                text("""
                    SELECT 1
                    FROM phone_numbers
                    WHERE emp_id = :emp_id AND phone_number = :phone_number
                """),
                {"emp_id": data.emp_id, "phone_number": data.phone_number}
            )

            if duplicate_exists.fetchone():
                logger.warning(f"Duplicate phone {data.phone_number} for emp_id={data.emp_id}")
                raise HTTPException(
                    status_code=400,
                    detail="Phone number already exists for this employee."
                )

            # Insert new phone number
            await connection.execute(
                text("""
                    INSERT INTO phone_numbers (emp_id, phone_number)
                    VALUES (:emp_id, :phone_number)
                """),
                {"emp_id": data.emp_id, "phone_number": data.phone_number}
            )

            await connection.commit()
            logger.info(f"New phone {data.phone_number} added for emp_id={data.emp_id}")

        return {"status": "success", "message": "Phone number added successfully."}

    except HTTPException as e:
        logger.error(f"HTTPException while adding phone: {e.detail}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while adding phone: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.exception("Unexpected error while adding phone number")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
