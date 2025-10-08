from fastapi import FastAPI
from src import create_user, add_phone, get_user, delete_user, update_salary

app = FastAPI(title="Employee Management API")

# Include routes from each module
app.include_router(create_user.router, prefix="/employee", tags=["Create User"])
app.include_router(add_phone.router, prefix="/employee", tags=["Phone Numbers"])
app.include_router(get_user.router, prefix="/employee", tags=["Get User"])
app.include_router(delete_user.router, prefix="/employee", tags=["Delete User"])
app.include_router(update_salary.router, prefix="/employee", tags=["Update Salary"])





