from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.database import Base

# Your test DB credentials (can be in .env.test)
TEST_DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/test_prc"

# Create a new engine for the test database
engine = create_engine(TEST_DATABASE_URL)

# Create a new SessionLocal for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables fresh for each test run
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
