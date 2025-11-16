import os
import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from typing import Generator
from sqlalchemy.orm import Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:example@localhost:5432/postgres"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def wait_for_db(max_retries: int = 30, delay: int = 1)  -> bool:
    """Wait for database to be ready"""
    for attempt in range(max_retries):
        try:
            connection = engine.connect()
            connection.close()
            print(f"Database connected successfully on attempt {attempt + 1}")
            return True
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {e}")
                time.sleep(delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise
    return False

def init_db() -> None:
    """Initialize database tables"""
    wait_for_db()
    Base.metadata.create_all(bind=engine)