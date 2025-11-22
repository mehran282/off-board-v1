"""Data validation utilities"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class FlyerData(BaseModel):
    """Validation schema for flyer data"""
    retailerId: str
    title: str = Field(..., min_length=1)
    pages: int = Field(..., gt=0)
    validFrom: datetime
    validUntil: datetime
    url: str
    pdfUrl: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    contentId: Optional[str] = None
    publishedFrom: Optional[datetime] = None
    publishedUntil: Optional[datetime] = None

    @validator("validUntil")
    def validate_dates(cls, v, values):
        if "validFrom" in values and v < values["validFrom"]:
            raise ValueError("validUntil must be after validFrom")
        return v


class OfferData(BaseModel):
    """Validation schema for offer data"""
    retailerId: str
    productName: str = Field(..., min_length=1)
    currentPrice: float = Field(..., gt=0)
    url: str
    flyerId: Optional[str] = None
    productId: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    oldPrice: Optional[float] = None
    discount: Optional[float] = None
    discountPercentage: Optional[float] = None
    unitPrice: Optional[str] = None
    imageUrl: Optional[str] = None
    validUntil: Optional[datetime] = None
    validFrom: Optional[datetime] = None
    description: Optional[str] = None
    contentId: Optional[str] = None
    parentContentId: Optional[str] = None
    pageNumber: Optional[int] = None
    publisherId: Optional[str] = None
    priceFormatted: Optional[str] = None
    oldPriceFormatted: Optional[str] = None
    priceFrequency: Optional[str] = None
    priceConditions: Optional[str] = None
    imageAlt: Optional[str] = None
    imageTitle: Optional[str] = None


class RetailerData(BaseModel):
    """Validation schema for retailer data"""
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    logoUrl: Optional[str] = None


class StoreData(BaseModel):
    """Validation schema for store data"""
    retailerId: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    postalCode: str = Field(..., min_length=1)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    openingHours: Optional[str] = None
