"""CLI script to run all spiders"""
import sys
import os
import json
from datetime import datetime, UTC
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add parent directory to path
scraper_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.dirname(scraper_dir)
sys.path.insert(0, parent_dir)  # Add project root to path
sys.path.insert(0, scraper_dir)  # Add scraper directory to path

# Change to scraper directory for Scrapy (where scrapy.cfg is)
os.chdir(scraper_dir)

from database.session import get_db_session
from models import ScrapingLog


def main():
    """Run all spiders"""
    log_id = None
    
    try:
        # Create scraping log
        with get_db_session() as session:
            log = ScrapingLog(
                type="all",
                status="running",
                startedAt=datetime.now(UTC),
                itemsScraped=0,
            )
            session.add(log)
            session.commit()
            log_id = log.id

        # Get Scrapy settings (must be in scraper directory where scrapy.cfg is)
        settings = get_project_settings()
        settings.set("USER_AGENT", "kaufda-scraper/1.0")

        # Create crawler process
        process = CrawlerProcess(settings)

        # Add all spiders
        process.crawl("retailers")
        process.crawl("flyers")
        process.crawl("offers")

        # Start crawling
        print("\n" + "=" * 80)
        print("🚀 Starting scraping process...")
        print("=" * 80 + "\n")
        process.start()

        # Get final statistics
        with get_db_session() as session:
            log = session.query(ScrapingLog).filter(ScrapingLog.id == log_id).first()
            if log:
                log.status = "completed"
                log.completedAt = datetime.now(UTC)
                session.commit()
                
                # Calculate duration
                duration = (log.completedAt - log.startedAt).total_seconds()
                
                # Get actual counts from database
                from models import Flyer, Offer, Retailer, Store
                flyers_count = session.query(Flyer).count()
                offers_count = session.query(Offer).count()
                retailers_count = session.query(Retailer).count()
                stores_count = session.query(Store).count()
                
                # Print final summary
                print("\n" + "=" * 80)
                print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
                print("=" * 80)
                print(f"\n📊 Final Statistics:")
                print(f"   • Items scraped (this run): {log.itemsScraped}")
                print(f"   • Duration: {int(duration // 60)}m {int(duration % 60)}s ({duration:.2f}s)")
                if duration > 0:
                    rate = log.itemsScraped / duration
                    print(f"   • Average speed: {rate:.2f} items/second")
                
                print(f"\n📦 Database Totals:")
                print(f"   • Flyers: {flyers_count}")
                print(f"   • Offers: {offers_count}")
                print(f"   • Retailers: {retailers_count}")
                print(f"   • Stores: {stores_count}")
                print(f"   • Total: {flyers_count + offers_count + retailers_count + stores_count}")
                
                print(f"\n⏰ Started: {log.startedAt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print(f"⏰ Completed: {log.completedAt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print("=" * 80 + "\n")

    except Exception as e:
        print(f"Scraping failed: {e}")
        
        # Update log with error
        if log_id:
            try:
                with get_db_session() as session:
                    log = session.query(ScrapingLog).filter(ScrapingLog.id == log_id).first()
                    if log:
                        log.status = "failed"
                        log.completedAt = datetime.now(UTC)
                        log.errors = json.dumps([str(e)])
                        session.commit()
            except:
                pass

        sys.exit(1)


if __name__ == "__main__":
    main()
