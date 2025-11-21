"""Check latest scraping log with details"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from models import ScrapingLog

try:
    with get_db_session() as session:
        # Get all logs ordered by startedAt
        logs = session.query(ScrapingLog).order_by(
            ScrapingLog.startedAt.desc()
        ).limit(5).all()
        
        print(f"Found {len(logs)} recent logs:\n")
        for i, log in enumerate(logs, 1):
            print(f"{i}. ID: {log.id[:20]}...")
            print(f"   Type: {log.type}")
            print(f"   Status: {log.status}")
            print(f"   Items Scraped: {log.itemsScraped}")
            print(f"   Started: {log.startedAt}")
            print(f"   Completed: {log.completedAt}")
            if log.errors:
                import json
                errors = json.loads(log.errors) if isinstance(log.errors, str) else log.errors
                print(f"   Errors: {errors[:2] if isinstance(errors, list) else errors}")
            print()
except Exception as e:
    print(f"Error: {e}")

