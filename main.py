from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from src.routes import user_routes
from src.db.database import SessionLocal, engine, Base
from src.db.models import EmailVerification
from src.core.logger import logger
from src.routes.slot_generator import generate_barber_slots  
from src.routes.shop_routes import router as shop_router
from src.routes.barber_routes import router as barber_router
from src.routes.availability_routes import router as availability_router
from src.routes.slot_generator import generate_barber_slots
from src.routes.booking_routes import router as booking_router
from fastapi.middleware.cors import CORSMiddleware


# Create all tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Online Booking App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)
# Include routes
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
#app.include_router(barber.router, prefix="/barber", tags=["Barber Slots"])
#app.include_router(bookings.router, prefix="/booking", tags=["Booking Slots"])
app.include_router(shop_router)
app.include_router(barber_router)
app.include_router(availability_router)
app.include_router(booking_router)


# Function to delete expired OTPs
def delete_expired_otps():
    db = SessionLocal()
    now = datetime.utcnow()
    try:
        deleted = db.query(EmailVerification).filter(
            EmailVerification.otp_expiry < now
        ).delete(synchronize_session=False)
        db.commit()
        logger.info(f"[OTP CLEANUP] Deleted {deleted} expired OTP(s) at {now}")
    except Exception as e:
        db.rollback()
        logger.error(f"[OTP CLEANUP ERROR] {str(e)}")
    finally:
        db.close()


# APScheduler instance
scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    try:
        # OTP Cleanup Job
        scheduler.add_job( 
            delete_expired_otps,
            "interval",
            minutes=5,
            id="delete_otps",
            replace_existing=True
        )

        # Barber Slot Generation Job
        scheduler.add_job(
            generate_barber_slots,
            "interval",
            minutes=60,   # runs once every 60 minutes
            id="slot_agent",
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started with OTP cleanup + Slot generator jobs")
    except Exception as e:
        logger.error(f" Failed to start scheduler: {str(e)}")


@app.on_event("shutdown")
def shutdown_scheduler():
    try:
        scheduler.shutdown()
        logger.info("Scheduler shutdown successfully.")
    except Exception as e:
        logger.error(f" Error while shutting down scheduler: {str(e)}")


@app.get("/")
def root():
    logger.info("Root endpoint '/' accessed.")
    return {"message": "Online Booking App Running!"}
