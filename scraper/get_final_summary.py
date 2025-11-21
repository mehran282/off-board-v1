"""Get final scraping summary with details"""
import sys
import os
import json
from datetime import datetime, UTC

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from models import Flyer, Offer, Retailer, ScrapingLog

try:
    with get_db_session() as session:
        # Get all completed logs
        completed_logs = session.query(ScrapingLog).filter(
            ScrapingLog.status == "completed"
        ).order_by(ScrapingLog.startedAt.desc()).limit(5).all()
        
        # Get running logs
        running_logs = session.query(ScrapingLog).filter(
            ScrapingLog.status == "running"
        ).order_by(ScrapingLog.startedAt.desc()).all()
        
        print("=" * 60)
        print("خلاصه نهایی Scraping")
        print("=" * 60)
        
        # Latest log
        latest_log = session.query(ScrapingLog).order_by(
            ScrapingLog.startedAt.desc()
        ).first()
        
        if latest_log:
            print(f"\n📊 آخرین Log:")
            print(f"   Status: {latest_log.status}")
            print(f"   Items Scraped (طبق log): {latest_log.itemsScraped}")
            print(f"   شروع: {latest_log.startedAt}")
            if latest_log.completedAt:
                duration = (latest_log.completedAt - latest_log.startedAt).total_seconds()
                print(f"   پایان: {latest_log.completedAt}")
                print(f"   مدت زمان: {int(duration)} ثانیه")
            else:
                duration = (datetime.now(UTC) - latest_log.startedAt).total_seconds()
                print(f"   در حال اجرا: {int(duration)} ثانیه")
        
        # Actual database counts
        print(f"\n📦 تعداد واقعی در دیتابیس:")
        flyers_count = session.query(Flyer).count()
        offers_count = session.query(Offer).count()
        retailers_count = session.query(Retailer).count()
        total_count = flyers_count + offers_count + retailers_count
        
        print(f"   🗞️  Flyers (پروپکت‌ها): {flyers_count}")
        print(f"   🏷️  Offers (آفرها): {offers_count}")
        print(f"   🏪 Retailers (فروشگاه‌ها): {retailers_count}")
        print(f"   📊 مجموع: {total_count}")
        
        # Retailers with details
        print(f"\n🏪 جزئیات فروشگاه‌ها:")
        retailers = session.query(Retailer).all()
        for retailer in retailers:
            flyer_count = session.query(Flyer).filter(Flyer.retailerId == retailer.id).count()
            offer_count = session.query(Offer).filter(Offer.retailerId == retailer.id).count()
            print(f"   • {retailer.name}: {flyer_count} پروپکت، {offer_count} آفر")
        
        # Sample offers
        if offers_count > 0:
            print(f"\n🏷️  نمونه آفرها:")
            sample_offers = session.query(Offer).limit(5).all()
            for offer in sample_offers:
                retailer = session.query(Retailer).filter(Retailer.id == offer.retailerId).first()
                retailer_name = retailer.name if retailer else "Unknown"
                print(f"   • {offer.productName} - {offer.currentPrice} € ({retailer_name})")
        
        # Running logs
        if running_logs:
            print(f"\n⏳ Logs در حال اجرا: {len(running_logs)}")
            for log in running_logs:
                duration = (datetime.now(UTC) - log.startedAt).total_seconds()
                print(f"   • Started: {log.startedAt}, Items: {log.itemsScraped}, Duration: {int(duration)}s")
        
        # Completed logs summary
        if completed_logs:
            print(f"\n✅ Logs تکمیل شده: {len(completed_logs)}")
            total_completed_items = sum(log.itemsScraped for log in completed_logs)
            print(f"   مجموع items در logs تکمیل شده: {total_completed_items}")
        
        print("\n" + "=" * 60)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

