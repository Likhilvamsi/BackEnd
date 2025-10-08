# app/routers/employees.py
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from db.database import async_engine  
from core.logger import logger   

router = APIRouter()

@router.get("/{name}")
async def get_users_by_name(name: str):
    try:
        logger.info(f"Fetching user(s) with name: {name}")

        async with async_engine.connect() as connection:
            query = text("SELECT * FROM employee_details WHERE first_name = :name")
            result = await connection.execute(query, {"name": name})
            rows = result.fetchall()

            result_list = [dict(row._mapping) for row in rows]

            if result_list:
                logger.info(f"Found {len(result_list)} user(s) with name: {name}")
                return {"status": "success", "users": result_list}
            else:
                logger.warning(f"No users found with name: {name}")
                return {"status": "success", "message": "No users found with that name"}

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching name={name}: {str(e)}")
        return JSONResponse(
            content={"status": "error", "message": "Internal server error"},
            status_code=500
        )
