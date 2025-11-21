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
        process.start()

        # Update log with final status
        with get_db_session() as session:
            log = session.query(ScrapingLog).filter(ScrapingLog.id == log_id).first()
            if log:
                log.status = "completed"
                log.completedAt = datetime.now(UTC)
                # Final items count will be updated by pipelines
                session.commit()

        print("Scraping completed successfully!")

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
