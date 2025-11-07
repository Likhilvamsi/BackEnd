from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from src.routes import user_routes
from src.db.database import SessionLocal, engine, Base
from src.db.models import EmailVerification
from src.core.logger import logger
from src.routes.slot_generator import generate_barber_slots  
from src.routes.shop_routes import router as shop_router
from src.routes.barber_routes import router as barber_router
from src.routes.availability_routes import router as availability_router
from src.routes.booking_routes import router as booking_router

# ============================================
# 🧱 Database initialization
# ============================================
Base.metadata.create_all(bind=engine)

# ============================================
# 🚀 FastAPI app initialization
# ============================================
app = FastAPI(
    title="Online Booking App",
    description="FastAPI backend for Flutter booking application",
    version="1.0.0"
)

# ============================================
# 🌐 Enable CORS for mobile + web access
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use ["https://135.237.191.7.nip.io"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 🧾 Log every incoming request
# ============================================
logging.basicConfig(
    filename="/home/azureuser/app/backend/api_access.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_ip = request.client.host
    method = request.method
    url = str(request.url.path)
    try:
        response = await call_next(request)
        status_code = response.status_code
        logging.info(f"{client_ip} - {method} {url} - {status_code}")
        return response
    except Exception as e:
        logging.error(f"{client_ip} - {method} {url} - ERROR: {str(e)}")
        raise e

# ============================================
# 🧩 Include Routers
# ============================================
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(shop_router)
app.include_router(barber_router)
app.include_router(availability_router)
app.include_router(booking_router)

# ============================================
# 🧹 OTP Cleanup Job
# ============================================
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

# ============================================
# ⏰ APScheduler setup
# ============================================
scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    try:
        scheduler.add_job(
            delete_expired_otps,
            "interval",
            minutes=5,
            id="delete_otps",
            replace_existing=True
        )

        scheduler.add_job(
            generate_barber_slots,
            "interval",
            minutes=60,
            id="slot_agent",
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started with OTP cleanup + Slot generator jobs")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")

@app.on_event("shutdown")
def shutdown_scheduler():
    try:
        scheduler.shutdown()
        logger.info("Scheduler shutdown successfully.")
    except Exception as e:
        logger.error(f"Error while shutting down scheduler: {str(e)}")

# ============================================
# 🌍 Health Check Endpoint
# ============================================
@app.get("/", tags=["Health"])
def root():
    logger.info("Root endpoint '/' accessed.")
    return {"message": "Online Booking App Running!", "status": "OK"}
