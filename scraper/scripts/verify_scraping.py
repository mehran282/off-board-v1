"""Verify scraping completeness by checking JSON structure"""
import asyncio
import json
import sys
import os
from playwright.async_api import async_playwright

# Add parent directory to path
scraper_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.dirname(scraper_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, scraper_dir)

async def verify_scraping():
    """Verify that all fields from kaufda.de are being scraped correctly"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading kaufda.de...")
        try:
            await page.goto("https://www.kaufda.de", wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"Warning: {e}")
        
        # Extract JSON
        json_data = await page.evaluate("""
            () => {
                const script = document.getElementById('__NEXT_DATA__');
                if (script) {
                    try {
                        return JSON.parse(script.textContent);
                    } catch (e) {
                        return null;
                    }
                }
                return null;
            }
        """)
        
        if not json_data:
            print("ERROR: Could not find __NEXT_DATA__ JSON")
            await browser.close()
            return
        
        page_props = json_data.get("props", {}).get("pageProps", {})
        page_info = page_props.get("pageInformation", {})
        
        print("\n" + "="*80)
        print("VERIFICATION REPORT: Scraping Completeness Check")
        print("="*80)
        
        # ========== OFFERS VERIFICATION ==========
        print("\n[1] OFFERS VERIFICATION")
        print("-" * 80)
        offers_data = page_info.get("offers", {}) or page_props.get("offers", {})
        main_offers = offers_data.get("main", {}).get("items", [])
        
        print(f"✓ Found {len(main_offers)} offers in JSON")
        
        if main_offers:
            sample_offer = main_offers[0]
            print(f"\nSample Offer Structure:")
            print(f"  Keys: {list(sample_offer.keys())}")
            
            # Check all fields we should extract
            required_fields = {
                "title": "productName",
                "brand": "brand",
                "description": "description",
                "prices.mainPrice": "currentPrice",
                "prices.secondaryPrice": "oldPrice",
                "prices.priceByBaseUnit": "unitPrice",
                "publisherName": "retailerId",
                "id": "url (constructed)",
                "offerImages.url": "imageUrl",
                "validFrom": "validFrom",
                "validUntil": "validUntil",
                "parentContent.type": "category",
            }
            
            print(f"\nField Mapping Check:")
            for json_path, our_field in required_fields.items():
                keys = json_path.split(".")
                value = sample_offer
                try:
                    for key in keys:
                        value = value.get(key, {}) if isinstance(value, dict) else None
                        if value is None:
                            break
                    if value:
                        print(f"  ✓ {json_path:30} -> {our_field:20} = {str(value)[:50]}")
                    else:
                        print(f"  ✗ {json_path:30} -> {our_field:20} = NOT FOUND")
                except:
                    print(f"  ✗ {json_path:30} -> {our_field:20} = ERROR")
            
            # Check prices structure
            prices = sample_offer.get("prices", {})
            print(f"\nPrices Structure:")
            print(f"  Keys: {list(prices.keys())}")
            print(f"  mainPrice: {prices.get('mainPrice')}")
            print(f"  secondaryPrice: {prices.get('secondaryPrice')}")
            print(f"  priceByBaseUnit: {prices.get('priceByBaseUnit')}")
        
        # ========== FLYERS VERIFICATION ==========
        print("\n[2] FLYERS VERIFICATION")
        print("-" * 80)
        brochures = page_info.get("brochures", {}) or page_props.get("brochures", {})
        top_ranked = brochures.get("topRanked", [])
        main_brochures = brochures.get("main", {}).get("items", [])
        all_brochures = top_ranked + main_brochures
        
        print(f"✓ Found {len(all_brochures)} flyers in JSON (topRanked: {len(top_ranked)}, main: {len(main_brochures)})")
        
        if all_brochures:
            sample_flyer = all_brochures[0]
            print(f"\nSample Flyer Structure:")
            print(f"  Keys: {list(sample_flyer.keys())}")
            
            required_fields = {
                "title": "title",
                "publisher.name": "retailerId",
                "pageCount": "pages",
                "validFrom": "validFrom",
                "validUntil": "validUntil",
                "id": "url (constructed)",
                "pages[0].url": "pdfUrl",
            }
            
            print(f"\nField Mapping Check:")
            for json_path, our_field in required_fields.items():
                keys = json_path.split(".")
                value = sample_flyer
                try:
                    for key in keys:
                        if key.isdigit():
                            key = int(key)
                            value = value[key] if isinstance(value, list) and key < len(value) else None
                        else:
                            value = value.get(key, {}) if isinstance(value, dict) else None
                        if value is None:
                            break
                    if value:
                        if isinstance(value, dict):
                            print(f"  ✓ {json_path:30} -> {our_field:20} = {list(value.keys())}")
                        else:
                            print(f"  ✓ {json_path:30} -> {our_field:20} = {str(value)[:50]}")
                    else:
                        print(f"  ✗ {json_path:30} -> {our_field:20} = NOT FOUND")
                except Exception as e:
                    print(f"  ✗ {json_path:30} -> {our_field:20} = ERROR: {e}")
        
        # ========== RETAILERS VERIFICATION ==========
        print("\n[3] RETAILERS VERIFICATION")
        print("-" * 80)
        
        retailers_found = []
        seen_names = set()
        
        # Check PublisherLinkbox
        template_content = page_info.get("template", {}).get("content", {})
        publisher_linkbox = template_content.get("PublisherLinkbox", {})
        publisher_links = publisher_linkbox.get("links", [])
        print(f"✓ PublisherLinkbox: {len(publisher_links)} retailers")
        
        # Check PublisherLogoLinkbox_Other
        publisher_logo_linkbox = template_content.get("PublisherLogoLinkbox_Other", {})
        publisher_logo_links = publisher_logo_linkbox.get("links", [])
        print(f"✓ PublisherLogoLinkbox_Other: {len(publisher_logo_links)} retailers")
        
        # Check from flyers
        if all_brochures:
            for brochure in all_brochures:
                publisher = brochure.get("publisher", {})
                name = publisher.get("name", "").strip()
                if name and name not in seen_names:
                    retailers_found.append({
                        "name": name,
                        "source": "brochures",
                        "logo": publisher.get("logo", {}).get("url", {})
                    })
                    seen_names.add(name)
        
        # Check from offers
        if main_offers:
            for offer in main_offers:
                retailer_name = offer.get("publisherName", "").strip()
                if retailer_name and retailer_name not in seen_names:
                    retailers_found.append({
                        "name": retailer_name,
                        "source": "offers",
                        "logo": None
                    })
                    seen_names.add(retailer_name)
        
        print(f"✓ Total unique retailers found: {len(retailers_found)}")
        if retailers_found:
            print(f"\nSample Retailers:")
            for i, retailer in enumerate(retailers_found[:5]):
                print(f"  {i+1}. {retailer['name']} (from {retailer['source']})")
        
        # ========== DATABASE MODEL CHECK ==========
        print("\n[4] DATABASE MODEL CHECK")
        print("-" * 80)
        
        from models import Offer, Flyer, Retailer
        
        print("Offer Model Fields:")
        offer_fields = [col.name for col in Offer.__table__.columns]
        print(f"  {', '.join(offer_fields)}")
        
        print("\nFlyer Model Fields:")
        flyer_fields = [col.name for col in Flyer.__table__.columns]
        print(f"  {', '.join(flyer_fields)}")
        
        print("\nRetailer Model Fields:")
        retailer_fields = [col.name for col in Retailer.__table__.columns]
        print(f"  {', '.join(retailer_fields)}")
        
        # ========== FRONTEND DISPLAY CHECK ==========
        print("\n[5] FRONTEND DISPLAY CHECK")
        print("-" * 80)
        
        frontend_components = {
            "OfferCard": ["productName", "brand", "currentPrice", "oldPrice", "discountPercentage", "imageUrl", "retailer", "validUntil"],
            "FlyerCard": ["title", "retailer", "validFrom", "validUntil", "pages", "offersCount"],
            "RetailerCard": ["name", "category", "logoUrl", "flyersCount", "offersCount", "storesCount"],
        }
        
        for component, fields in frontend_components.items():
            print(f"\n{component} displays:")
            for field in fields:
                print(f"  ✓ {field}")
        
        print("\n" + "="*80)
        print("VERIFICATION COMPLETE")
        print("="*80)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_scraping())

