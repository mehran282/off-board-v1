"""Base model for SQLAlchemy"""
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Abstract base model with common fields"""
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    createdAt = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updatedAt = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

