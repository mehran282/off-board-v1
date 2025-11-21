"""Product model"""
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Product(BaseModel):
    """Product model matching Prisma schema"""
    __tablename__ = "Product"

    name = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=True, index=True)
    category = Column(String, nullable=True, index=True)
    description = Column(String, nullable=True)
    imageUrl = Column(String, nullable=True)
    scrapedAt = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    offers = relationship("Offer", back_populates="product")

