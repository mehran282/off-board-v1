"""Check scraping status"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from models import ScrapingLog

try:
    with get_db_session() as session:
        log = session.query(ScrapingLog).filter(
            ScrapingLog.status == "running"
        ).order_by(ScrapingLog.startedAt.desc()).first()
        
        if log:
            print(f"Status: {log.status}")
            print(f"Items Scraped: {log.itemsScraped}")
            print(f"Started At: {log.startedAt}")
            print(f"Type: {log.type}")
        else:
            # Get latest log
            latest = session.query(ScrapingLog).order_by(
                ScrapingLog.startedAt.desc()
            ).first()
            if latest:
                print(f"Latest Log - Status: {latest.status}, Items: {latest.itemsScraped}, Started: {latest.startedAt}")
            else:
                print("No logs found")
except Exception as e:
    print(f"Error: {e}")

