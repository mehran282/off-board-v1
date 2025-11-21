"""Check Product and Store counts in database"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from models import Product, Store, Offer

try:
    with get_db_session() as session:
        print("=" * 60)
        print("بررسی Product و Store در دیتابیس")
        print("=" * 60)
        
        # Count Products
        products_count = session.query(Product).count()
        print(f"\n📦 تعداد Product: {products_count}")
        
        # Count Stores
        stores_count = session.query(Store).count()
        print(f"🏪 تعداد Store: {stores_count}")
        
        # Count Offers with Product
        offers_with_product = session.query(Offer).filter(Offer.productId.isnot(None)).count()
        total_offers = session.query(Offer).count()
        print(f"\n🏷️  Offers با Product: {offers_with_product} از {total_offers}")
        
        # Sample Products
        if products_count > 0:
            print(f"\n📦 نمونه Productها:")
            sample_products = session.query(Product).limit(5).all()
            for product in sample_products:
                offer_count = session.query(Offer).filter(Offer.productId == product.id).count()
                print(f"   • {product.name} (Brand: {product.brand or 'N/A'}, Offers: {offer_count})")
        
        # Sample Stores
        if stores_count > 0:
            print(f"\n🏪 نمونه Storeها:")
            sample_stores = session.query(Store).limit(5).all()
            for store in sample_stores:
                print(f"   • {store.address}, {store.city} {store.postalCode} (Retailer ID: {store.retailerId})")
        else:
            print(f"\n⚠️  هیچ Store پیدا نشد!")
        
        # Offers without Product
        offers_without_product = session.query(Offer).filter(Offer.productId.is_(None)).count()
        if offers_without_product > 0:
            print(f"\n⚠️  {offers_without_product} Offer بدون Product وجود دارد!")
            sample_offers = session.query(Offer).filter(Offer.productId.is_(None)).limit(3).all()
            print("   نمونه Offerهای بدون Product:")
            for offer in sample_offers:
                print(f"   • {offer.productName} - {offer.url}")
        
        print("\n" + "=" * 60)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

