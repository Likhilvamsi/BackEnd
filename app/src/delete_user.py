from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db.database import async_engine
from core.logger import logger

router = APIRouter()

@router.delete("/{emp_id}")
async def delete_user(emp_id: int):
    try:
        logger.info(f"Attempting to delete employee with ID: {emp_id}")

        # Use async with for async engine
        async with async_engine.begin() as connection:
            # Check if employee exists
            emp_exists = await connection.execute(
                text("SELECT 1 FROM employee_details WHERE emp_id = :emp_id"),
                {"emp_id": emp_id}
            )
            emp_exists = emp_exists.fetchone()

            if not emp_exists:
                logger.warning(f"Employee ID {emp_id} not found for deletion")
                raise HTTPException(status_code=404, detail=f"Employee with id {emp_id} not found.")

            # Delete related records first
            await connection.execute(text("DELETE FROM emails WHERE emp_id = :emp_id"), {"emp_id": emp_id})
            await connection.execute(text("DELETE FROM addresses WHERE emp_id = :emp_id"), {"emp_id": emp_id})
            await connection.execute(text("DELETE FROM phone_numbers WHERE emp_id = :emp_id"), {"emp_id": emp_id})

            # Delete main employee record
            await connection.execute(text("DELETE FROM employee_details WHERE emp_id = :emp_id"), {"emp_id": emp_id})

            logger.info(f"Employee with ID {emp_id} and related records deleted successfully")

        return {
            "status": "success",
            "message": f"Employee with id {emp_id} and related records deleted successfully."
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting employee {emp_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error while deleting employee {emp_id}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
