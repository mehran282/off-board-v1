"""ScrapingLog model"""
from datetime import datetime, UTC
from sqlalchemy import Column, String, Integer, DateTime, Index
from .base import BaseModel


class ScrapingLog(BaseModel):
    """ScrapingLog model matching Prisma schema"""
    __tablename__ = "ScrapingLog"

    type = Column(String, nullable=False, index=True)  # 'flyers' | 'offers' | 'retailers' | 'products' | 'all'
    status = Column(String, nullable=False, index=True)  # 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
    startedAt = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    completedAt = Column(DateTime, nullable=True)
    itemsScraped = Column(Integer, default=0, nullable=False)
    errors = Column(String, nullable=True)  # JSON array of error messages
    metadata_json = Column('metadata', String, nullable=True)  # JSON object for additional data (using 'metadata' as column name to match Prisma schema)

