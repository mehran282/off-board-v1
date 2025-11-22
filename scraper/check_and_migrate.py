"""Check database schema and apply migrations if needed"""
from database.connection import engine
from sqlalchemy import text, inspect

def check_columns():
    """Check if new columns exist"""
    inspector = inspect(engine)
    
    # Check Flyer table
    flyer_columns = [col['name'] for col in inspector.get_columns('Flyer')]
    print("Flyer columns:", sorted(flyer_columns))
    
    # Check Offer table
    offer_columns = [col['name'] for col in inspector.get_columns('Offer')]
    print("Offer columns:", sorted(offer_columns))
    
    # Check which new columns are missing
    flyer_new = ['contentId', 'publishedFrom', 'publishedUntil']
    offer_new = [
        'contentId', 'parentContentId', 'pageNumber', 'publisherId',
        'priceFormatted', 'oldPriceFormatted', 'priceFrequency',
        'priceConditions', 'imageAlt', 'imageTitle', 'description', 'validFrom'
    ]
    
    missing_flyer = [col for col in flyer_new if col not in flyer_columns]
    missing_offer = [col for col in offer_new if col not in offer_columns]
    
    if missing_flyer:
        print(f"\nMissing Flyer columns: {missing_flyer}")
    else:
        print("\nAll Flyer columns exist!")
    
    if missing_offer:
        print(f"Missing Offer columns: {missing_offer}")
    else:
        print("All Offer columns exist!")
    
    return missing_flyer, missing_offer

def apply_migrations(missing_flyer, missing_offer):
    """Apply SQL migrations"""
    if not missing_flyer and not missing_offer:
        print("\nNo migrations needed!")
        return
    
    conn = engine.connect()
    trans = conn.begin()
    
    try:
        # Add Flyer columns
        if 'contentId' in missing_flyer:
            conn.execute(text("ALTER TABLE \"Flyer\" ADD COLUMN \"contentId\" TEXT"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS \"Flyer_contentId_idx\" ON \"Flyer\"(\"contentId\")"))
            print("Added contentId to Flyer")
        
        if 'publishedFrom' in missing_flyer:
            conn.execute(text("ALTER TABLE \"Flyer\" ADD COLUMN \"publishedFrom\" TIMESTAMP(3)"))
            print("Added publishedFrom to Flyer")
        
        if 'publishedUntil' in missing_flyer:
            conn.execute(text("ALTER TABLE \"Flyer\" ADD COLUMN \"publishedUntil\" TIMESTAMP(3)"))
            print("Added publishedUntil to Flyer")
        
        # Add Offer columns
        if 'contentId' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"contentId\" TEXT"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS \"Offer_contentId_idx\" ON \"Offer\"(\"contentId\")"))
            print("Added contentId to Offer")
        
        if 'parentContentId' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"parentContentId\" TEXT"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS \"Offer_parentContentId_idx\" ON \"Offer\"(\"parentContentId\")"))
            print("Added parentContentId to Offer")
        
        if 'pageNumber' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"pageNumber\" INTEGER"))
            print("Added pageNumber to Offer")
        
        if 'publisherId' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"publisherId\" TEXT"))
            print("Added publisherId to Offer")
        
        if 'priceFormatted' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"priceFormatted\" TEXT"))
            print("Added priceFormatted to Offer")
        
        if 'oldPriceFormatted' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"oldPriceFormatted\" TEXT"))
            print("Added oldPriceFormatted to Offer")
        
        if 'priceFrequency' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"priceFrequency\" TEXT"))
            print("Added priceFrequency to Offer")
        
        if 'priceConditions' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"priceConditions\" TEXT"))
            print("Added priceConditions to Offer")
        
        if 'imageAlt' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"imageAlt\" TEXT"))
            print("Added imageAlt to Offer")
        
        if 'imageTitle' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"imageTitle\" TEXT"))
            print("Added imageTitle to Offer")
        
        if 'description' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"description\" TEXT"))
            print("Added description to Offer")
        
        if 'validFrom' in missing_offer:
            conn.execute(text("ALTER TABLE \"Offer\" ADD COLUMN \"validFrom\" TIMESTAMP(3)"))
            print("Added validFrom to Offer")
        
        trans.commit()
        print("\nMigrations applied successfully!")
        
    except Exception as e:
        trans.rollback()
        print(f"\nError applying migrations: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Checking database schema...")
    missing_flyer, missing_offer = check_columns()
    
    if missing_flyer or missing_offer:
        print("\nApplying migrations...")
        apply_migrations(missing_flyer, missing_offer)
    else:
        print("\nDatabase is up to date!")

