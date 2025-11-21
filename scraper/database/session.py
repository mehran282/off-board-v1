"""Session management"""
import sys
import os
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, Session

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database.connection import engine
from models import Base

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

