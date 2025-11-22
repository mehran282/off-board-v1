"""Check if new fields are being scraped and saved"""
from database.connection import engine
from sqlalchemy import text

def check_flyers():
    """Check Flyer table for new fields"""
    conn = engine.connect()
    result = conn.execute(text('''
        SELECT "contentId", "publishedFrom", "publishedUntil", "title"
        FROM "Flyer"
        WHERE "contentId" IS NOT NULL
        LIMIT 3
    '''))
    rows = result.fetchall()
    conn.close()
    
    if rows:
        print("Sample Flyers with new fields:")
        for row in rows:
            print(f"  - {row[3]}: contentId={row[0]}, publishedFrom={row[1]}, publishedUntil={row[2]}")
    else:
        print("No Flyers with new fields found yet")
    
    return len(rows)

def check_offers():
    """Check Offer table for new fields"""
    conn = engine.connect()
    result = conn.execute(text('''
        SELECT "contentId", "parentContentId", "pageNumber", "publisherId", 
               "priceFormatted", "imageAlt", "productName"
        FROM "Offer"
        WHERE "contentId" IS NOT NULL
        LIMIT 3
    '''))
    rows = result.fetchall()
    conn.close()
    
    if rows:
        print("\nSample Offers with new fields:")
        for row in rows:
            print(f"  - {row[6]}: contentId={row[0]}, parentContentId={row[1]}, "
                  f"pageNumber={row[2]}, publisherId={row[3]}, priceFormatted={row[4]}, imageAlt={row[5]}")
    else:
        print("\nNo Offers with new fields found yet")
    
    return len(rows)

if __name__ == "__main__":
    print("Checking scraped data for new fields...\n")
    flyer_count = check_flyers()
    offer_count = check_offers()
    
    print(f"\nSummary: {flyer_count} flyers and {offer_count} offers with new fields")

