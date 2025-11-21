"""Test JSON extraction from kaufda.de"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_json_extraction():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading kaufda.de...")
        try:
            await page.goto("https://www.kaufda.de", wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"Warning: {e}")
        
        # Try to extract JSON
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
        
        print("\n=== JSON Structure Found ===")
        
        # Check brochures
        brochures = json_data.get("props", {}).get("pageProps", {}).get("brochures", {})
        main_brochures = brochures.get("main", {}).get("items", [])
        print(f"Brochures (Flyers): {len(main_brochures)} items")
        if main_brochures:
            print(f"  First flyer: {main_brochures[0].get('title', 'N/A')}")
            print(f"  Publisher: {main_brochures[0].get('publisher', {}).get('name', 'N/A')}")
            print(f"  Pages: {main_brochures[0].get('pageCount', 'N/A')}")
        
        # Check offers
        offers_data = json_data.get("props", {}).get("pageProps", {}).get("offers", {})
        main_offers = offers_data.get("main", {}).get("items", [])
        print(f"\nOffers: {len(main_offers)} items")
        if main_offers:
            print(f"  First offer: {main_offers[0].get('title', 'N/A')}")
            print(f"  Price: {main_offers[0].get('prices', {}).get('mainPrice', 'N/A')} €")
            print(f"  Publisher: {main_offers[0].get('publisherName', 'N/A')}")
        
        # Check retailers
        publisher_linkbox = json_data.get("props", {}).get("pageProps", {}).get("PublisherLinkbox", {})
        publisher_links = publisher_linkbox.get("links", [])
        print(f"\nRetailers (PublisherLinkbox): {len(publisher_links)} items")
        if publisher_links:
            print(f"  First retailer: {publisher_links[0].get('link_text', 'N/A')}")
        
        await browser.close()
        print("\n=== Test completed successfully ===")

if __name__ == "__main__":
    asyncio.run(test_json_extraction())

