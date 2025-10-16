from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
