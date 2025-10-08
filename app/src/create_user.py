from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr, condecimal
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db.database import async_engine as engine 
from core.logger import logger   
import re
import time   # <-- for profiling

router = APIRouter()

class EmployeeCreate(BaseModel):
    emp_id: int | None = None
    first_name: constr(pattern=r"^[A-Za-z]+$", strip_whitespace=True)
    last_name: constr(pattern=r"^[A-Za-z]+$", strip_whitespace=True)
    date_of_birth: str
    salary: condecimal(gt=0, max_digits=10, decimal_places=2)
    status: constr(pattern=r"^(Active|Inactive)$")


@router.post("/")
async def create_user(employee: EmployeeCreate):
    start_time = time.perf_counter()  # start profiling
    try:
        # Validate date format (YYYY-MM-DD)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", employee.date_of_birth):
            logger.warning(f"Invalid DOB format received: {employee.date_of_birth}")
            raise HTTPException(
                status_code=400,
                detail="Date of birth must be in YYYY-MM-DD format"
            )

        validation_time = time.perf_counter()
        logger.debug(f"Validation took {validation_time - start_time:.4f} seconds")

        async with engine.begin() as connection:
            # Check if emp_id already exists (if provided)
            if employee.emp_id is not None:
                emp_exists = await connection.execute(
                    text("SELECT 1 FROM employee_details WHERE emp_id = :emp_id"),
                    {"emp_id": employee.emp_id}
                )
                if emp_exists.fetchone():
                    logger.warning(f"Duplicate emp_id attempted: {employee.emp_id}")
                    raise HTTPException(status_code=400, detail="Employee ID already exists.")

            empid_check_time = time.perf_counter()
            logger.debug(f"emp_id check took {empid_check_time - validation_time:.4f} seconds")

            # Check duplicate by name + dob
            duplicate_exists = await connection.execute(
                text("""
                    SELECT 1
                    FROM employee_details
                    WHERE first_name = :first_name
                      AND last_name = :last_name
                      AND date_of_birth = :dob
                """),
                {
                    "first_name": employee.first_name,
                    "last_name": employee.last_name,
                    "dob": employee.date_of_birth
                }
            )

            if duplicate_exists.fetchone():
                logger.warning(
                    f"Duplicate employee detected: {employee.first_name} {employee.last_name}, DOB {employee.date_of_birth}"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Employee with the same name and date of birth already exists."
                )

            duplicate_check_time = time.perf_counter()
            logger.debug(f"Duplicate check took {duplicate_check_time - empid_check_time:.4f} seconds")

            # Insert new employee
            if employee.emp_id is None:
                await connection.execute(
                    text("""
                        INSERT INTO employee_details
                            (first_name, last_name, date_of_birth, salary, status)
                        VALUES
                            (:first_name, :last_name, :dob, :salary, :status)
                    """),
                    {
                        "first_name": employee.first_name,
                        "last_name": employee.last_name,
                        "dob": employee.date_of_birth,
                        "salary": employee.salary,
                        "status": employee.status
                    }
                )
                logger.info(f"New employee created: {employee.first_name} {employee.last_name}")
            else:
                await connection.execute(
                    text("""
                        INSERT INTO employee_details
                            (emp_id, first_name, last_name, date_of_birth, salary, status)
                        VALUES
                            (:emp_id, :first_name, :last_name, :dob, :salary, :status)
                    """),
                    {
                        "emp_id": employee.emp_id,
                        "first_name": employee.first_name,
                        "last_name": employee.last_name,
                        "dob": employee.date_of_birth,
                        "salary": employee.salary,
                        "status": employee.status
                    }
                )
                logger.info(f"Employee with emp_id={employee.emp_id} created.")

        total_time = time.perf_counter()
        logger.info(f"Employee creation completed in {total_time - start_time:.4f} seconds")

        return {"status": "success", "message": "Employee added successfully."}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error while creating employee")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
