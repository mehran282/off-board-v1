"""Retailer model"""
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Retailer(BaseModel):
    """Retailer model matching Prisma schema"""
    __tablename__ = "Retailer"

    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    logoUrl = Column(String, nullable=True)
    scrapedAt = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    flyers = relationship("Flyer", back_populates="retailer", cascade="all, delete-orphan")
    stores = relationship("Store", back_populates="retailer", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="retailer", cascade="all, delete-orphan")

