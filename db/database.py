import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.logger import logger  # central logger

# Load environment variables
load_dotenv()

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

# Async database URL (using aiomysql)
DATABASE_URL = f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}"

# Create async engine
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for models
Base = declarative_base()

# Dependency for async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Opening async database session")
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()
            logger.info("Async database session closed")
