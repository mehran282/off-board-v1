"""Get detailed scraping summary"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from models import Flyer, Offer, Retailer, ScrapingLog

try:
    with get_db_session() as session:
        # Get latest log
        latest_log = session.query(ScrapingLog).order_by(
            ScrapingLog.startedAt.desc()
        ).first()
        
        if latest_log:
            print(f"=== Latest Scraping Log ===")
            print(f"ID: {latest_log.id}")
            print(f"Type: {latest_log.type}")
            print(f"Status: {latest_log.status}")
            print(f"Items Scraped (from log): {latest_log.itemsScraped}")
            print(f"Started: {latest_log.startedAt}")
            print(f"Completed: {latest_log.completedAt}")
            if latest_log.errors:
                errors = json.loads(latest_log.errors) if isinstance(latest_log.errors, str) else latest_log.errors
                print(f"Errors: {len(errors) if isinstance(errors, list) else 0}")
        
        # Get actual counts from database
        print(f"\n=== Actual Database Counts ===")
        flyers_count = session.query(Flyer).count()
        offers_count = session.query(Offer).count()
        retailers_count = session.query(Retailer).count()
        
        print(f"Flyers: {flyers_count}")
        print(f"Offers: {offers_count}")
        print(f"Retailers: {retailers_count}")
        print(f"Total: {flyers_count + offers_count + retailers_count}")
        
        # Get some sample data
        print(f"\n=== Sample Data ===")
        if flyers_count > 0:
            sample_flyer = session.query(Flyer).first()
            print(f"Sample Flyer: {sample_flyer.title} (Retailer: {sample_flyer.retailerId})")
        
        if offers_count > 0:
            sample_offer = session.query(Offer).first()
            print(f"Sample Offer: {sample_offer.productName} - {sample_offer.currentPrice} € (Retailer: {sample_offer.retailerId})")
        
        if retailers_count > 0:
            sample_retailer = session.query(Retailer).first()
            print(f"Sample Retailer: {sample_retailer.name} ({sample_retailer.category})")
        
        # Get retailers with counts
        print(f"\n=== Retailers Breakdown ===")
        retailers = session.query(Retailer).all()
        for retailer in retailers[:10]:  # First 10
            flyer_count = session.query(Flyer).filter(Flyer.retailerId == retailer.id).count()
            offer_count = session.query(Offer).filter(Offer.retailerId == retailer.id).count()
            print(f"  {retailer.name}: {flyer_count} flyers, {offer_count} offers")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

