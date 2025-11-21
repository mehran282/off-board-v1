"""Store model"""
from datetime import datetime, UTC
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class Store(BaseModel):
    """Store model matching Prisma schema"""
    __tablename__ = "Store"

    retailerId = Column(String, ForeignKey("Retailer.id", ondelete="CASCADE"), nullable=False, index=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    postalCode = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone = Column(String, nullable=True)
    openingHours = Column(String, nullable=True)  # JSON string
    scrapedAt = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    retailer = relationship("Retailer", back_populates="stores")

    __table_args__ = (
        UniqueConstraint('retailerId', 'address', name='store_retailer_address_unique'),
    )

