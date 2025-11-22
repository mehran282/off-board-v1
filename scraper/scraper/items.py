"""Scrapy items"""
import scrapy
from typing import Optional
from datetime import datetime


class FlyerItem(scrapy.Item):
    """Item for flyer data"""
    retailerId = scrapy.Field()
    title = scrapy.Field()
    pages = scrapy.Field()
    validFrom = scrapy.Field()
    validUntil = scrapy.Field()
    url = scrapy.Field()
    pdfUrl = scrapy.Field(required=False)
    thumbnailUrl = scrapy.Field(required=False)
    contentId = scrapy.Field(required=False)
    publishedFrom = scrapy.Field(required=False)
    publishedUntil = scrapy.Field(required=False)


class OfferItem(scrapy.Item):
    """Item for offer data"""
    flyerId = scrapy.Field(required=False)
    productId = scrapy.Field(required=False)
    retailerId = scrapy.Field()
    productName = scrapy.Field()
    brand = scrapy.Field(required=False)
    category = scrapy.Field(required=False)
    currentPrice = scrapy.Field()
    oldPrice = scrapy.Field(required=False)
    discount = scrapy.Field(required=False)
    discountPercentage = scrapy.Field(required=False)
    unitPrice = scrapy.Field(required=False)
    url = scrapy.Field()
    imageUrl = scrapy.Field(required=False)
    validUntil = scrapy.Field(required=False)
    validFrom = scrapy.Field(required=False)
    description = scrapy.Field(required=False)
    contentId = scrapy.Field(required=False)
    parentContentId = scrapy.Field(required=False)
    pageNumber = scrapy.Field(required=False)
    publisherId = scrapy.Field(required=False)
    priceFormatted = scrapy.Field(required=False)
    oldPriceFormatted = scrapy.Field(required=False)
    priceFrequency = scrapy.Field(required=False)
    priceConditions = scrapy.Field(required=False)
    imageAlt = scrapy.Field(required=False)
    imageTitle = scrapy.Field(required=False)


class RetailerItem(scrapy.Item):
    """Item for retailer data"""
    name = scrapy.Field()
    category = scrapy.Field()
    logoUrl = scrapy.Field(required=False)


class StoreItem(scrapy.Item):
    """Item for store data"""
    retailerId = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    postalCode = scrapy.Field()
    latitude = scrapy.Field(required=False)
    longitude = scrapy.Field(required=False)
    phone = scrapy.Field(required=False)
    openingHours = scrapy.Field(required=False)  # JSON string
