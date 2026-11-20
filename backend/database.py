import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL with fallback to local SQLite for immediate zero-config demo
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "investigation.db"))
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Ensure directory exists for sqlite file
if DATABASE_URL.startswith("sqlite"):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
