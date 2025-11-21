"""CLI script to run offers spider"""
import sys
import os
import json
from datetime import datetime, UTC
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from models import ScrapingLog


def main():
    """Run offers spider"""
    log_id = None
    
    try:
        # Create scraping log
        with get_db_session() as session:
            log = ScrapingLog(
                type="offers",
                status="running",
                startedAt=datetime.now(UTC),
                itemsScraped=0,
            )
            session.add(log)
            session.commit()
            log_id = log.id

        # Get Scrapy settings
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        settings = get_project_settings()
        settings.set("USER_AGENT", "kaufda-scraper/1.0")

        # Create crawler process
        process = CrawlerProcess(settings)
        process.crawl("offers")
        process.start()

        # Update log
        with get_db_session() as session:
            log = session.query(ScrapingLog).filter(ScrapingLog.id == log_id).first()
            if log:
                log.status = "completed"
                log.completedAt = datetime.now(UTC)
                session.commit()

        print("Offer scraping completed successfully!")

    except Exception as e:
        print(f"Offer scraping failed: {e}")
        
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

