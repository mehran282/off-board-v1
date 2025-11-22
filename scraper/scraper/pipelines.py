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
    """Prevent duplicate entries using in-memory cache and database check"""

    def __init__(self):
        self.seen_urls = set()  # In-memory cache for current run
        self.seen_content_ids = set()  # In-memory cache for contentId

    def open_spider(self, spider):
        """Load existing URLs and contentIds from database to prevent re-scraping"""
        try:
            with get_db_session() as session:
                # Load existing flyer URLs and contentIds
                flyers = session.query(Flyer.url, Flyer.contentId).all()
                for url, content_id in flyers:
                    if url:
                        self.seen_urls.add(url)
                    if content_id:
                        self.seen_content_ids.add(content_id)
                
                # Load existing offer URLs and contentIds
                offers = session.query(Offer.url, Offer.contentId).all()
                for url, content_id in offers:
                    if url:
                        self.seen_urls.add(url)
                    if content_id:
                        self.seen_content_ids.add(content_id)
                
                spider.logger.info(f"DeduplicationPipeline: Loaded {len(self.seen_urls)} URLs and {len(self.seen_content_ids)} contentIds from database")
        except Exception as e:
            spider.logger.warning(f"DeduplicationPipeline: Could not load existing URLs from database: {e}")

    def process_item(self, item, spider):
        """Check for duplicates by URL or contentId"""
        url = item.get("url")
        content_id = item.get("contentId")
        
        # Check by URL
        if url and url in self.seen_urls:
            spider.logger.debug(f"Duplicate item skipped (by URL): {url}")
            return None
        
        # Check by contentId (for flyers and offers)
        if content_id and content_id in self.seen_content_ids:
            spider.logger.debug(f"Duplicate item skipped (by contentId): {content_id}")
            return None

        # Add to cache
        if url:
            self.seen_urls.add(url)
        if content_id:
            self.seen_content_ids.add(content_id)

        return item


class DatabasePipeline:
    """Save items to database"""

    def __init__(self):
        self.retailer_cache: Dict[str, str] = {}  # name -> id
        self.product_cache: Dict[str, str] = {}  # (name, brand) -> id
        self.saved_items_count = 0
        self.updated_items_count = 0
        self.created_items_count = 0
        self.failed_items_count = 0
        self.items_by_type: Dict[str, int] = {
            "retailers": 0,
            "flyers": 0,
            "offers": 0,
            "stores": 0,
        }
        self.log_id = None
        self.start_time = None

    def open_spider(self, spider):
        """Open database session"""
        self.Session = get_db_session()
        self.start_time = datetime.now(UTC)
        self.logger = spider.logger  # Store logger for use in private methods
        spider.logger.info("=" * 80)
        spider.logger.info(f"🚀 DatabasePipeline: Spider '{spider.name}' started")
        spider.logger.info(f"⏰ Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        spider.logger.info("=" * 80)
        
        # Find running log entry
        try:
            with get_db_session() as session:
                log = session.query(ScrapingLog).filter(
                    ScrapingLog.status == "running"
                ).order_by(ScrapingLog.startedAt.desc()).first()
                if log:
                    self.log_id = log.id
                    spider.logger.info(f"📝 Connected to ScrapingLog ID: {self.log_id}")
        except Exception as e:
            spider.logger.warning(f"⚠️  Could not find running log entry: {e}")

    def process_item(self, item, spider):
        """Save item to database"""
        item_type = None
        item_created = False
        item_updated = False
        
        try:
            with get_db_session() as session:
                if "name" in item:  # RetailerItem
                    item_type = "retailers"
                    result = self._save_retailer(item, session)
                    item_created = result.get("created", False)
                    item_updated = result.get("updated", False)
                elif "title" in item:  # FlyerItem
                    item_type = "flyers"
                    result = self._save_flyer(item, session)
                    item_created = result.get("created", False)
                    item_updated = result.get("updated", False)
                elif "productName" in item:  # OfferItem
                    item_type = "offers"
                    result = self._save_offer(item, session)
                    item_created = result.get("created", False)
                    item_updated = result.get("updated", False)
                elif "address" in item and "retailerId" in item:  # StoreItem
                    item_type = "stores"
                    try:
                        result = self._save_store(item, session)
                        item_created = result.get("created", False)
                        item_updated = result.get("updated", False)
                    except ValueError as e:
                        spider.logger.error(f"❌ Failed to save store: {e}")
                        spider.logger.error(f"   Store data: retailerId={item.get('retailerId')}, address={item.get('address')}, city={item.get('city')}")
                        raise  # Re-raise to be caught by outer exception handler

                # Note: commit is handled by get_db_session context manager
                self.saved_items_count += 1
                
                if item_created:
                    self.created_items_count += 1
                if item_updated:
                    self.updated_items_count += 1
                
                if item_type:
                    self.items_by_type[item_type] = self.items_by_type.get(item_type, 0) + 1
                
                # Log every item with details
                item_name = item.get('url') or item.get('name') or item.get('title') or item.get('productName') or 'unknown'
                status_icon = "✨" if item_created else "🔄" if item_updated else "💾"
                spider.logger.info(f"{status_icon} [{item_type or 'unknown'}] {status_icon} {item_name[:80]}")
                
                # Update ScrapingLog every 10 items to avoid too many database writes
                if self.log_id and self.saved_items_count % 10 == 0:
                    self._update_scraping_log(spider)
                    elapsed = (datetime.now(UTC) - self.start_time).total_seconds() if self.start_time else 0
                    rate = self.saved_items_count / elapsed if elapsed > 0 else 0
                    spider.logger.info(f"📈 Progress: {self.saved_items_count} items saved | {rate:.2f} items/sec | Created: {self.created_items_count} | Updated: {self.updated_items_count}")
                    
        except IntegrityError as e:
            self.failed_items_count += 1
            item_name = item.get('url') or item.get('name') or item.get('title') or 'unknown'
            spider.logger.warning(f"⚠️  Duplicate/Integrity error for {item_name}: {str(e)[:100]}")
            # Note: rollback is handled by get_db_session context manager
        except Exception as e:
            self.failed_items_count += 1
            item_name = item.get('url') or item.get('name') or item.get('title') or 'unknown'
            spider.logger.error(f"❌ Error saving {item_name}: {str(e)[:200]}")
            import traceback
            spider.logger.error(f"❌ Full traceback:\n{traceback.format_exc()}")
            # Note: rollback is handled by get_db_session context manager
            # Do not re-raise, allow other items to be processed

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
        """Save retailer to database - MUST be called before saving stores"""
        name = item["name"]
        created = False
        updated = False
        
        # Check cache first
        if name in self.retailer_cache:
            retailer_id = self.retailer_cache[name]
            self.logger.debug(f"Retailer '{name}' found in cache (ID: {retailer_id})")
            return {"id": retailer_id, "created": False, "updated": False}

        # Check if exists
        retailer = session.query(Retailer).filter(Retailer.name == name).first()
        if not retailer:
            retailer = Retailer(
                name=name,
                category=item.get("category", "General"),
                logoUrl=item.get("logoUrl"),
            )
            session.add(retailer)
            session.flush()  # Get ID - IMPORTANT: flush to ensure retailer is available for stores
            created = True
            self.logger.info(f"✨ Created retailer '{name}' (ID: {retailer.id})")
        else:
            # Update existing retailer
            if item.get("logoUrl") and item.get("logoUrl") != retailer.logoUrl:
                retailer.logoUrl = item.get("logoUrl")
                updated = True
            self.logger.debug(f"Retailer '{name}' already exists (ID: {retailer.id})")
        
        # Cache retailer ID - IMPORTANT: cache after flush to ensure ID is available
        self.retailer_cache[name] = retailer.id
        return {"id": retailer.id, "created": created, "updated": updated}

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
            flyer.title = item["title"]
            flyer.pages = item["pages"]
            flyer.validFrom = item["validFrom"]
            flyer.validUntil = item["validUntil"]
            if item.get("pdfUrl"):
                flyer.pdfUrl = normalize_url(item["pdfUrl"])
            if item.get("thumbnailUrl"):
                flyer.thumbnailUrl = normalize_url(item["thumbnailUrl"])
            if item.get("contentId"):
                flyer.contentId = item["contentId"]
            if item.get("publishedFrom"):
                flyer.publishedFrom = item["publishedFrom"]
            if item.get("publishedUntil"):
                flyer.publishedUntil = item["publishedUntil"]
            flyer.scrapedAt = datetime.now(UTC)
            return {"id": flyer.id, "created": False, "updated": True}

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
        return {"id": flyer.id, "created": True, "updated": False}

    def _save_offer(self, item: Dict[str, Any], session):
        """Save offer to database"""
        url = normalize_url(item["url"])

        # Check if exists - try by URL first, then by contentId if available
        offer = session.query(Offer).filter(Offer.url == url).first()
        
        # If not found by URL and we have contentId, try to find by contentId
        if not offer and item.get("contentId"):
            offer = session.query(Offer).filter(Offer.contentId == item["contentId"]).first()
        
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
            return {"id": offer.id, "created": False, "updated": True}

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
        return {"id": offer.id, "created": True, "updated": False}

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
        """Save store to database - REQUIRES retailer to be saved first"""
        retailer_id = item.get("retailerId")
        address = item.get("address", "").strip()
        
        if not retailer_id or not address:
            self.logger.warning(f"Store item missing required fields: retailerId={retailer_id}, address={address}")
            raise ValueError("Retailer ID and address are required for store")
        
        # Convert retailer name to ID if needed
        # IMPORTANT: Check cache first (retailers should be saved before stores)
        if isinstance(retailer_id, str) and retailer_id not in self.retailer_cache:
            # Retailer not in cache - try to find it in database
            retailer = session.query(Retailer).filter(Retailer.name == retailer_id).first()
            if retailer:
                # Found in database - add to cache
                self.retailer_cache[retailer_id] = retailer.id
                retailer_id = retailer.id
                self.logger.debug(f"Found retailer '{retailer_id}' in database (not in cache)")
            else:
                # Retailer not found - create it as fallback (shouldn't happen if order is correct)
                self.logger.warning(f"⚠️  Retailer '{retailer_id}' not found in cache or database, creating it as fallback...")
                try:
                    new_retailer = Retailer(
                        name=retailer_id,
                        category="General",
                    )
                    session.add(new_retailer)
                    session.flush()  # Flush to get ID
                    self.retailer_cache[retailer_id] = new_retailer.id
                    retailer_id = new_retailer.id
                    self.logger.info(f"✨ Created retailer '{retailer_id}' as fallback for store")
                except Exception as e:
                    self.logger.error(f"❌ Failed to create retailer '{retailer_id}': {e}")
                    raise ValueError(f"Retailer '{retailer_id}' not found and could not be created: {e}")
        elif retailer_id in self.retailer_cache:
            # Retailer in cache - use cached ID
            retailer_id = self.retailer_cache[retailer_id]
            self.logger.debug(f"Using cached retailer ID for '{item.get('retailerId')}': {retailer_id}")
        
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
            return {"id": store.id, "created": False, "updated": True}
        
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
        return {"id": store.id, "created": True, "updated": False}

    def close_spider(self, spider):
        """Close database session and log final statistics"""
        end_time = datetime.now(UTC)
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        spider.logger.info("")
        spider.logger.info("=" * 80)
        spider.logger.info(f"✅ DatabasePipeline: Spider '{spider.name}' finished")
        spider.logger.info(f"⏰ End time: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        spider.logger.info(f"⏱️  Duration: {int(duration // 60)}m {int(duration % 60)}s ({duration:.2f}s total)")
        spider.logger.info("")
        spider.logger.info("📊 Statistics:")
        spider.logger.info(f"   ✅ Created: {self.created_items_count}")
        spider.logger.info(f"   🔄 Updated: {self.updated_items_count}")
        spider.logger.info(f"   ❌ Failed: {self.failed_items_count}")
        spider.logger.info(f"   📦 Total saved: {self.saved_items_count}")
        spider.logger.info("")
        spider.logger.info("📋 Items by type:")
        for item_type, count in self.items_by_type.items():
            if count > 0:
                spider.logger.info(f"   • {item_type.capitalize()}: {count}")
        if duration > 0:
            rate = self.saved_items_count / duration
            spider.logger.info(f"")
            spider.logger.info(f"⚡ Speed: {rate:.2f} items/second")
        spider.logger.info("=" * 80)
        
        self.Session.remove()

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
        self.start_time = None

    def open_spider(self, spider):
        """Called when spider opens"""
        self.start_time = datetime.now(UTC)
        spider.logger.info("")
        spider.logger.info("=" * 80)
        spider.logger.info(f"🕷️  Spider '{spider.name}' started")
        spider.logger.info(f"⏰ Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        spider.logger.info("=" * 80)
        
        # Try to find the latest running log entry
        try:
            with get_db_session() as session:
                log = session.query(ScrapingLog).filter(
                    ScrapingLog.status == "running"
                ).order_by(ScrapingLog.startedAt.desc()).first()
                if log:
                    self.log_id = log.id
                    spider.logger.info(f"📝 Connected to ScrapingLog ID: {self.log_id}")
        except Exception as e:
            spider.logger.warning(f"⚠️  Could not find running log entry: {e}")

    def close_spider(self, spider):
        """Called when spider closes"""
        end_time = datetime.now(UTC)
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        spider.logger.info("")
        spider.logger.info("=" * 80)
        spider.logger.info(f"✅ Spider '{spider.name}' finished")
        spider.logger.info(f"📊 Items processed: {self.items_count}")
        spider.logger.info(f"⏰ End time: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        spider.logger.info(f"⏱️  Duration: {int(duration // 60)}m {int(duration % 60)}s ({duration:.2f}s total)")
        if duration > 0 and self.items_count > 0:
            rate = self.items_count / duration
            spider.logger.info(f"⚡ Processing rate: {rate:.2f} items/second")
        spider.logger.info("=" * 80)
        
        # Update log with final count
        if self.log_id:
            try:
                with get_db_session() as session:
                    log = session.query(ScrapingLog).filter(ScrapingLog.id == self.log_id).first()
                    if log:
                        log.itemsScraped = (log.itemsScraped or 0) + self.items_count
                        session.commit()
                        spider.logger.info(f"📝 Updated ScrapingLog ID {self.log_id}: {log.itemsScraped} total items")
            except Exception as e:
                spider.logger.error(f"❌ Failed to update log entry: {e}")

    def process_item(self, item, spider):
        """Log item processing and update ScrapingLog in real-time"""
        self.items_count += 1
        
        # Update log every 20 items to avoid too many database writes
        if self.log_id and self.items_count % 20 == 0:
            try:
                with get_db_session() as session:
                    log = session.query(ScrapingLog).filter(ScrapingLog.id == self.log_id).first()
                    if log:
                        log.itemsScraped = (log.itemsScraped or 0) + 20
                        session.commit()
                        elapsed = (datetime.now(UTC) - self.start_time).total_seconds() if self.start_time else 0
                        rate = self.items_count / elapsed if elapsed > 0 else 0
                        spider.logger.info(f"📈 Progress: {self.items_count} items processed | {rate:.2f} items/sec")
            except Exception as e:
                spider.logger.warning(f"⚠️  Failed to update log entry: {e}")
        
        return item
