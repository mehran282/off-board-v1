"""Test detailed JSON structure"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_json_detailed():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading kaufda.de...")
        try:
            await page.goto("https://www.kaufda.de", wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(15000)  # Wait longer for dynamic content
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
            print("ERROR: Could not find __NEXT_DATA__")
            await browser.close()
            return
        
        # Navigate through the structure
        props = json_data.get("props", {})
        page_props = props.get("pageProps", {})
        
        print("\n=== Available keys in pageProps ===")
        print(list(page_props.keys())[:20])
        
        # Check brochures with different paths
        print("\n=== Checking Brochures ===")
        if "brochures" in page_props:
            brochures = page_props["brochures"]
            print(f"Brochures type: {type(brochures)}")
            print(f"Brochures keys: {list(brochures.keys()) if isinstance(brochures, dict) else 'N/A'}")
            if isinstance(brochures, dict):
                main = brochures.get("main", {})
                print(f"Main keys: {list(main.keys()) if isinstance(main, dict) else 'N/A'}")
                if isinstance(main, dict):
                    items = main.get("items", [])
                    print(f"Items count: {len(items)}")
                    if items:
                        print(f"First item keys: {list(items[0].keys())[:10]}")
        
        # Check offers
        print("\n=== Checking Offers ===")
        if "offers" in page_props:
            offers = page_props["offers"]
            print(f"Offers type: {type(offers)}")
            print(f"Offers keys: {list(offers.keys()) if isinstance(offers, dict) else 'N/A'}")
            if isinstance(offers, dict):
                main = offers.get("main", {})
                print(f"Main keys: {list(main.keys()) if isinstance(main, dict) else 'N/A'}")
                if isinstance(main, dict):
                    items = main.get("items", [])
                    print(f"Items count: {len(items)}")
                    if items:
                        print(f"First item keys: {list(items[0].keys())[:10]}")
        
        # Check retailers
        print("\n=== Checking Retailers ===")
        publisher_keys = [k for k in page_props.keys() if "publisher" in k.lower() or "linkbox" in k.lower()]
        print(f"Publisher-related keys: {publisher_keys}")
        
        for key in publisher_keys[:3]:
            data = page_props[key]
            if isinstance(data, dict):
                links = data.get("links", [])
                print(f"{key}: {len(links)} links")
                if links:
                    print(f"  First link: {links[0].get('link_text', 'N/A')}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_json_detailed())

