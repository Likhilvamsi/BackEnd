# update_salary.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db.database import async_engine as engine
from core.logger import logger   

router = APIRouter()

@router.put("/{emp_id}")
async def update_salary(emp_id: int, salary: float):
    try:
        async with engine.connect() as connection:
            logger.info(f"Checking if employee with ID {emp_id} exists...")  # log

            # Check if employee exists
            emp_exists = await connection.execute(
                text("SELECT 1 FROM employee_details WHERE emp_id = :emp_id"),
                {"emp_id": emp_id}
            )
            emp_exists = emp_exists.fetchone()

            if not emp_exists:
                logger.warning(f"Employee with ID {emp_id} not found.")  # log
                raise HTTPException(status_code=404, detail=f"Employee with id {emp_id} not found.")

            # Update salary
            logger.info(f"Updating salary for employee {emp_id} to {salary}...")  # log
            await connection.execute(
                text("UPDATE employee_details SET salary = :salary WHERE emp_id = :emp_id"),
                {"salary": salary, "emp_id": emp_id}
            )
            await connection.commit()

            logger.info(f"Salary for employee {emp_id} updated successfully.")  # log
            return {
                "status": "success",
                "message": f"Salary for employee id {emp_id} updated successfully to {salary}."
            }

    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")  # log
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating salary for {emp_id}: {str(e)}")  # log
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error while updating salary for {emp_id}")  # log full traceback
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
