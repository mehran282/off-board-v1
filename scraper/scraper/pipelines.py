"""Scrapy pipelines"""
import json
import logging
import sys
import os
from datetime import datetime, UTC
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database.session import get_db_session
from models import (
    Retailer,
    Flyer,
    Offer,
    Product,
    Store,
    ScrapingLog,
)
from utils.validators import FlyerData, OfferData, RetailerData, StoreData
from utils.helpers import normalize_url, extract_price, parse_date

logger = logging.getLogger(__name__)


class ValidationPipeline:
    """Validate scraped items"""

    def process_item(self, item, spider):
        """Validate item based on its type"""
        try:
            if "name" in item:  # RetailerItem
                validated = RetailerData(**item)
                return dict(validated)
            elif "title" in item:  # FlyerItem
                validated = FlyerData(**item)
                return dict(validated)
            elif "productName" in item:  # OfferItem
                validated = OfferData(**item)
                return dict(validated)
            elif "address" in item and "retailerId" in item:  # StoreItem
                validated = StoreData(**item)
                return dict(validated)
        except Exception as e:
            logger.warning(f"Validation failed for item: {e}")
            spider.logger.warning(f"Validation failed: {e}")
            return None

        return item


class DeduplicationPipeline:
    """Prevent duplicate entries"""

    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        """Check for duplicates"""
        url = item.get("url")
        if url and url in self.seen_urls:
            spider.logger.debug(f"Duplicate item skipped: {url}")
            return None

        if url:
            self.seen_urls.add(url)

        return item


class DatabasePipeline:
    """Save items to database"""

    def __init__(self):
        self.retailer_cache: Dict[str, str] = {}  # name -> id
        self.product_cache: Dict[str, str] = {}  # (name, brand) -> id
        self.saved_items_count = 0
        self.log_id = None

    def open_spider(self, spider):
        """Called when spider opens - find running log entry"""
        try:
            with get_db_session() as session:
                log = session.query(ScrapingLog).filter(
                    ScrapingLog.status == "running"
                ).order_by(ScrapingLog.startedAt.desc()).first()
                if log:
                    self.log_id = log.id
                    spider.logger.info(f"DatabasePipeline: Found running log entry: {self.log_id}")
        except Exception as e:
            spider.logger.warning(f"DatabasePipeline: Could not find running log entry: {e}")

    def process_item(self, item, spider):
        """Save item to database"""
        try:
            with get_db_session() as session:
                if "name" in item:  # RetailerItem
                    self._save_retailer(item, session)
                elif "title" in item:  # FlyerItem
                    self._save_flyer(item, session)
                elif "productName" in item:  # OfferItem
                    self._save_offer(item, session)
                elif "address" in item and "retailerId" in item:  # StoreItem
                    self._save_store(item, session)

                session.commit()
                self.saved_items_count += 1
                spider.logger.info(f"Saved item: {item.get('url', item.get('name', 'unknown'))}")
                
                # Update ScrapingLog every 5 items to avoid too many database writes
                if self.log_id and self.saved_items_count % 5 == 0:
                    self._update_scraping_log(spider)
        except IntegrityError as e:
            spider.logger.warning(f"Integrity error (likely duplicate): {e}")
            session.rollback()
        except Exception as e:
            spider.logger.error(f"Error saving item to database: {e}")
            session.rollback()
            raise

        return item

    def _update_scraping_log(self, spider):
        """Update ScrapingLog with current items count"""
        if not self.log_id:
            return
            
        try:
            with get_db_session() as session:
                log = session.query(ScrapingLog).filter(ScrapingLog.id == self.log_id).first()
                if log:
                    log.itemsScraped = self.saved_items_count
                    session.commit()
                    spider.logger.debug(f"Updated ScrapingLog: {self.saved_items_count} items scraped")
        except Exception as e:
            spider.logger.warning(f"Failed to update ScrapingLog: {e}")

    def _save_retailer(self, item: Dict[str, Any], session):
        """Save retailer to database"""
        name = item["name"]
        
        # Check cache first
        if name in self.retailer_cache:
            return self.retailer_cache[name]

        # Check if exists
        retailer = session.query(Retailer).filter(Retailer.name == name).first()
        if not retailer:
            retailer = Retailer(
                name=name,
                category=item.get("category", "General"),
                logoUrl=item.get("logoUrl"),
            )
            session.add(retailer)
            session.flush()  # Get ID

        self.retailer_cache[name] = retailer.id
        return retailer.id

    def _save_flyer(self, item: Dict[str, Any], session):
        """Save flyer to database"""
        url = normalize_url(item["url"])

        # Check if exists - try by URL first, then by contentId if available
        flyer = session.query(Flyer).filter(Flyer.url == url).first()
        
        # If not found by URL and we have contentId, try to find by contentId
        if not flyer and item.get("contentId"):
            flyer = session.query(Flyer).filter(Flyer.contentId == item["contentId"]).first()
        if flyer:
            # Update existing
            self.logger.debug(f"Updating existing flyer {flyer.id} with contentId: {item.get('contentId')}, publishedFrom: {item.get('publishedFrom')}")
            flyer.title = item["title"]
            flyer.pages = item["pages"]
            flyer.validFrom = item["validFrom"]
            flyer.validUntil = item["validUntil"]
            if item.get("pdfUrl"):
                flyer.pdfUrl = normalize_url(item["pdfUrl"])
            if item.get("thumbnailUrl"):
                flyer.thumbnailUrl = normalize_url(item["thumbnailUrl"])
                self.logger.debug(f"Updated flyer {flyer.id} with thumbnailUrl: {item['thumbnailUrl']}")
            if item.get("contentId"):
                flyer.contentId = item["contentId"]
                self.logger.debug(f"Updated flyer {flyer.id} with contentId: {item['contentId']}")
            if item.get("publishedFrom"):
                flyer.publishedFrom = item["publishedFrom"]
                self.logger.debug(f"Updated flyer {flyer.id} with publishedFrom: {item['publishedFrom']}")
            if item.get("publishedUntil"):
                flyer.publishedUntil = item["publishedUntil"]
                self.logger.debug(f"Updated flyer {flyer.id} with publishedUntil: {item['publishedUntil']}")
            flyer.scrapedAt = datetime.now(UTC)
            return flyer.id

        # Get retailer ID
        retailer_id = item.get("retailerId")
        if isinstance(retailer_id, str) and retailer_id not in self.retailer_cache:
            # Try to find retailer by name
            retailer = session.query(Retailer).filter(Retailer.name == retailer_id).first()
            if retailer:
                self.retailer_cache[retailer_id] = retailer.id
                retailer_id = retailer.id
            else:
                # Create retailer if not exists
                retailer = Retailer(name=retailer_id, category="General")
                session.add(retailer)
                session.flush()
                self.retailer_cache[retailer_id] = retailer.id
                retailer_id = retailer.id
        elif retailer_id in self.retailer_cache:
            retailer_id = self.retailer_cache[retailer_id]

        if not retailer_id:
            raise ValueError("Retailer ID is required for flyer")

        # Create new flyer
        self.logger.debug(f"Creating new flyer with contentId: {item.get('contentId')}, publishedFrom: {item.get('publishedFrom')}, thumbnailUrl: {item.get('thumbnailUrl')}")
        thumbnail_url = normalize_url(item["thumbnailUrl"]) if item.get("thumbnailUrl") else None
        self.logger.debug(f"Normalized thumbnailUrl: {thumbnail_url}")
        flyer = Flyer(
            retailerId=retailer_id,
            title=item["title"],
            pages=item["pages"],
            validFrom=item["validFrom"],
            validUntil=item["validUntil"],
            url=url,
            pdfUrl=normalize_url(item["pdfUrl"]) if item.get("pdfUrl") else None,
            thumbnailUrl=thumbnail_url,
            contentId=item.get("contentId"),
            publishedFrom=item.get("publishedFrom"),
            publishedUntil=item.get("publishedUntil"),
        )
        session.add(flyer)
        session.flush()
        self.logger.debug(f"Created flyer {flyer.id} with contentId: {flyer.contentId}, thumbnailUrl: {flyer.thumbnailUrl}")
        return flyer.id

    def _save_offer(self, item: Dict[str, Any], session):
        """Save offer to database"""
        url = normalize_url(item["url"])

        # Check if exists
        offer = session.query(Offer).filter(Offer.url == url).first()
        if offer:
            # Update existing
            offer.productName = item["productName"]
            offer.currentPrice = item["currentPrice"]
            offer.oldPrice = item.get("oldPrice")
            offer.discount = item.get("discount")
            offer.discountPercentage = item.get("discountPercentage")
            if item.get("description"):
                offer.description = item["description"]
            if item.get("validFrom"):
                offer.validFrom = item["validFrom"]
            if item.get("contentId"):
                offer.contentId = item["contentId"]
            if item.get("parentContentId"):
                offer.parentContentId = item["parentContentId"]
            if item.get("pageNumber") is not None:
                offer.pageNumber = item["pageNumber"]
            if item.get("publisherId"):
                offer.publisherId = item["publisherId"]
            if item.get("priceFormatted"):
                offer.priceFormatted = item["priceFormatted"]
            if item.get("oldPriceFormatted"):
                offer.oldPriceFormatted = item["oldPriceFormatted"]
            if item.get("priceFrequency"):
                offer.priceFrequency = item["priceFrequency"]
            if item.get("priceConditions"):
                offer.priceConditions = item["priceConditions"]
            if item.get("imageAlt"):
                offer.imageAlt = item["imageAlt"]
            if item.get("imageTitle"):
                offer.imageTitle = item["imageTitle"]
            # Update product relationship
            product_id = self._get_or_create_product(item, session)
            if product_id:
                offer.productId = product_id
            offer.scrapedAt = datetime.now(UTC)
            return offer.id

        # Get retailer ID
        retailer_id = item.get("retailerId")
        if isinstance(retailer_id, str) and retailer_id not in self.retailer_cache:
            retailer = session.query(Retailer).filter(Retailer.name == retailer_id).first()
            if retailer:
                self.retailer_cache[retailer_id] = retailer.id
                retailer_id = retailer.id
            else:
                retailer = Retailer(name=retailer_id, category=item.get("category", "General"))
                session.add(retailer)
                session.flush()
                self.retailer_cache[retailer_id] = retailer.id
                retailer_id = retailer.id
        elif retailer_id in self.retailer_cache:
            retailer_id = self.retailer_cache[retailer_id]

        if not retailer_id:
            raise ValueError("Retailer ID is required for offer")

        # Get flyer ID if provided (try by parentContentId first, then flyerId)
        flyer_id = item.get("flyerId")
        parent_content_id = item.get("parentContentId")
        if parent_content_id:
            # Try to find flyer by contentId
            flyer = session.query(Flyer).filter(Flyer.contentId == parent_content_id).first()
            if flyer:
                flyer_id = flyer.id
        elif flyer_id:
            flyer = session.query(Flyer).filter(Flyer.id == flyer_id).first()
            if not flyer:
                flyer_id = None

        # Get or create Product
        product_id = self._get_or_create_product(item, session)

        # Create new offer
        offer = Offer(
            flyerId=flyer_id,
            productId=product_id,
            retailerId=retailer_id,
            productName=item["productName"],
            brand=item.get("brand"),
            category=item.get("category"),
            currentPrice=item["currentPrice"],
            oldPrice=item.get("oldPrice"),
            discount=item.get("discount"),
            discountPercentage=item.get("discountPercentage"),
            unitPrice=item.get("unitPrice"),
            url=url,
            imageUrl=normalize_url(item["imageUrl"]) if item.get("imageUrl") else None,
            validUntil=item.get("validUntil"),
            validFrom=item.get("validFrom"),
            description=item.get("description"),
            contentId=item.get("contentId"),
            parentContentId=item.get("parentContentId"),
            pageNumber=item.get("pageNumber"),
            publisherId=item.get("publisherId"),
            priceFormatted=item.get("priceFormatted"),
            oldPriceFormatted=item.get("oldPriceFormatted"),
            priceFrequency=item.get("priceFrequency"),
            priceConditions=item.get("priceConditions"),
            imageAlt=item.get("imageAlt"),
            imageTitle=item.get("imageTitle"),
        )
        session.add(offer)
        session.flush()
        return offer.id

    def _get_or_create_product(self, item: Dict[str, Any], session) -> str:
        """Get or create Product from offer data"""
        product_name = item.get("productName", "").strip()
        if not product_name:
            return None
        
        brand = item.get("brand")
        cache_key = f"{product_name}|{brand or ''}"
        
        # Check cache first
        if cache_key in self.product_cache:
            return self.product_cache[cache_key]
        
        # Try to find existing product by name and brand
        query = session.query(Product).filter(Product.name == product_name)
        if brand:
            query = query.filter(Product.brand == brand)
        else:
            query = query.filter(Product.brand.is_(None))
        
        product = query.first()
        
        if not product:
            # Create new product
            product = Product(
                name=product_name,
                brand=brand,
                category=item.get("category"),
                description=item.get("description"),
                imageUrl=normalize_url(item["imageUrl"]) if item.get("imageUrl") else None,
            )
            session.add(product)
            session.flush()
        
        self.product_cache[cache_key] = product.id
        return product.id

    def _save_store(self, item: Dict[str, Any], session):
        """Save store to database"""
        retailer_id = item.get("retailerId")
        address = item.get("address", "").strip()
        
        if not retailer_id or not address:
            raise ValueError("Retailer ID and address are required for store")
        
        # Convert retailer name to ID if needed
        if isinstance(retailer_id, str) and retailer_id not in self.retailer_cache:
            retailer = session.query(Retailer).filter(Retailer.name == retailer_id).first()
            if retailer:
                self.retailer_cache[retailer_id] = retailer.id
                retailer_id = retailer.id
            else:
                raise ValueError(f"Retailer '{retailer_id}' not found")
        elif retailer_id in self.retailer_cache:
            retailer_id = self.retailer_cache[retailer_id]
        
        # Check if store exists (unique constraint on retailerId + address)
        store = session.query(Store).filter(
            Store.retailerId == retailer_id,
            Store.address == address
        ).first()
        
        if store:
            # Update existing store
            store.city = item.get("city", store.city)
            store.postalCode = item.get("postalCode", store.postalCode)
            store.latitude = item.get("latitude")
            store.longitude = item.get("longitude")
            store.phone = item.get("phone")
            store.openingHours = item.get("openingHours")
            store.scrapedAt = datetime.now(UTC)
            return store.id
        
        # Create new store
        store = Store(
            retailerId=retailer_id,
            address=address,
            city=item.get("city", ""),
            postalCode=item.get("postalCode", ""),
            latitude=item.get("latitude"),
            longitude=item.get("longitude"),
            phone=item.get("phone"),
            openingHours=item.get("openingHours"),
        )
        session.add(store)
        session.flush()
        return store.id

    def _update_scraping_log(self, spider):
        """Update ScrapingLog with current items count"""
        if not self.log_id:
            return
            
        try:
            with get_db_session() as session:
                log = session.query(ScrapingLog).filter(ScrapingLog.id == self.log_id).first()
                if log:
                    log.itemsScraped = self.saved_items_count
                    session.commit()
                    spider.logger.debug(f"Updated ScrapingLog: {self.saved_items_count} items scraped")
        except Exception as e:
            spider.logger.warning(f"Failed to update ScrapingLog: {e}")


class LoggingPipeline:
    """Log scraping progress and update ScrapingLog in real-time"""

    def __init__(self):
        """Initialize logging pipeline"""
        self.items_count = 0
        self.log_id = None

    def open_spider(self, spider):
        """Called when spider opens"""
        spider.logger.info(f"Spider {spider.name} started")
        
        # Try to find the latest running log entry
        try:
            with get_db_session() as session:
                log = session.query(ScrapingLog).filter(
                    ScrapingLog.status == "running"
                ).order_by(ScrapingLog.startedAt.desc()).first()
                if log:
                    self.log_id = log.id
                    spider.logger.info(f"Found running log entry: {self.log_id}")
        except Exception as e:
            spider.logger.warning(f"Could not find running log entry: {e}")

    def close_spider(self, spider):
        """Called when spider closes"""
        spider.logger.info(f"Spider {spider.name} finished, scraped {self.items_count} items")
        
        # Update log with final count
        if self.log_id:
            try:
                with get_db_session() as session:
                    log = session.query(ScrapingLog).filter(ScrapingLog.id == self.log_id).first()
                    if log:
                        log.itemsScraped = (log.itemsScraped or 0) + self.items_count
                        session.commit()
                        spider.logger.info(f"Updated log entry {self.log_id} with {self.items_count} items")
            except Exception as e:
                spider.logger.error(f"Failed to update log entry: {e}")

    def process_item(self, item, spider):
        """Log item processing and update ScrapingLog in real-time"""
        self.items_count += 1
        
        # Update log every 10 items to avoid too many database writes
        if self.log_id and self.items_count % 10 == 0:
            try:
                with get_db_session() as session:
                    log = session.query(ScrapingLog).filter(ScrapingLog.id == self.log_id).first()
                    if log:
                        log.itemsScraped = (log.itemsScraped or 0) + 10
                        session.commit()
                        spider.logger.debug(f"Updated log: {log.itemsScraped} items scraped so far")
            except Exception as e:
                spider.logger.warning(f"Failed to update log entry: {e}")
        
        spider.logger.debug(f"Processing item: {item.get('url', item.get('name', 'unknown'))}")
        return item
