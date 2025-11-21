"""Flyer model"""
from datetime import datetime, UTC
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Flyer(BaseModel):
    """Flyer model matching Prisma schema"""
    __tablename__ = "Flyer"

    retailerId = Column(String, ForeignKey("Retailer.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    pages = Column(Integer, nullable=False)
    validFrom = Column(DateTime, nullable=False, index=True)
    validUntil = Column(DateTime, nullable=False, index=True)
    url = Column(String, unique=True, nullable=False, index=True)
    pdfUrl = Column(String, nullable=True)
    scrapedAt = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    retailer = relationship("Retailer", back_populates="flyers")
    offers = relationship("Offer", back_populates="flyer")

