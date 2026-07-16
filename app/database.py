from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine (using NullPool if PgBouncer is active on port 6543)
if ":6543" in settings.DATABASE_URL:
    engine = create_engine(settings.DATABASE_URL, poolclass=NullPool)
else:
    engine = create_engine(settings.DATABASE_URL)

# Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()

# Dependency to get db session in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
