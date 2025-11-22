"""Offer model"""
from datetime import datetime, UTC
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Offer(BaseModel):
    """Offer model matching Prisma schema"""
    __tablename__ = "Offer"

    flyerId = Column(String, ForeignKey("Flyer.id", ondelete="SET NULL"), nullable=True, index=True)
    productId = Column(String, ForeignKey("Product.id", ondelete="SET NULL"), nullable=True, index=True)
    retailerId = Column(String, ForeignKey("Retailer.id", ondelete="CASCADE"), nullable=False, index=True)
    productName = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=True)
    category = Column(String, nullable=True)
    currentPrice = Column(Float, nullable=False, index=True)
    oldPrice = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    discountPercentage = Column(Float, nullable=True)
    unitPrice = Column(String, nullable=True)
    url = Column(String, unique=True, nullable=False, index=True)
    imageUrl = Column(String, nullable=True)
    validUntil = Column(DateTime, nullable=True, index=True)
    contentId = Column(String, nullable=True, index=True)
    parentContentId = Column(String, nullable=True, index=True)
    pageNumber = Column(Integer, nullable=True)
    publisherId = Column(String, nullable=True)
    priceFormatted = Column(String, nullable=True)
    oldPriceFormatted = Column(String, nullable=True)
    priceFrequency = Column(String, nullable=True)
    priceConditions = Column(String, nullable=True)  # JSON string
    imageAlt = Column(String, nullable=True)
    imageTitle = Column(String, nullable=True)
    description = Column(String, nullable=True)
    validFrom = Column(DateTime, nullable=True)
    scrapedAt = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    flyer = relationship("Flyer", back_populates="offers")
    product = relationship("Product", back_populates="offers")
    retailer = relationship("Retailer", back_populates="offers")

