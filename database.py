from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
import os
import re
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./music_app.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Supabase or external providers sometimes give postgres:// instead of postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Remove pgbouncer query parameter which psycopg2 rejects
    clean_url = DATABASE_URL.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")

    # Safely handle special characters in passwords (e.g. '@', '$', '*')
    match = re.match(r"^postgresql(?:\+psycopg2)?://([^:]+):(.*)@([^/@:]+)(?::(\d+))?/([^?]+)", clean_url)
    if match:
        user, password, host, port, dbname = match.groups()
        safe_url = URL.create(
            drivername="postgresql+psycopg2",
            username=user,
            password=password,
            host=host,
            port=int(port) if port else 5432,
            database=dbname,
        )
        engine = create_engine(safe_url)
    else:
        engine = create_engine(clean_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
