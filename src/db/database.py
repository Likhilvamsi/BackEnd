from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import DATABASE_URL
from src.core.logger import logger

try:
    engine = create_engine(DATABASE_URL, echo=True)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    logger.info("Creating new database session...")
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error during DB session: {e}")
        raise
    finally:
        db.close()
        logger.info("Database session closed")
