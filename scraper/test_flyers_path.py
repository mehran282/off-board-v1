"""Test flyers JSON path"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_flyers_path():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading kaufda.de...")
        try:
            await page.goto("https://www.kaufda.de", wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(15000)
        except Exception as e:
            print(f"Warning: {e}")
        
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
        
        # Test the path we're using
        page_props = json_data.get("props", {}).get("pageProps", {})
        page_info = page_props.get("pageInformation", {})
        brochures = page_info.get("brochures", {}) or page_props.get("brochures", {})
        main_brochures = brochures.get("main", {}).get("items", [])
        
        print(f"\n=== Flyers Path Test ===")
        print(f"pageInformation exists: {'pageInformation' in page_props}")
        print(f"brochures in pageInformation: {'brochures' in page_info}")
        print(f"brochures in pageProps: {'brochures' in page_props}")
        print(f"main_brochures count: {len(main_brochures)}")
        
        if len(main_brochures) == 0:
            # Try alternative paths
            print("\n=== Trying alternative paths ===")
            
            # Check topRanked
            top_ranked = brochures.get("topRanked", [])
            print(f"topRanked: {len(top_ranked)} items")
            if top_ranked:
                print(f"  First: {top_ranked[0].get('title', 'N/A')}")
            
            # Check all keys in brochures
            print(f"\nBrochures keys: {list(brochures.keys())}")
            
            # Check pageInformation structure
            print(f"\npageInformation keys: {list(page_info.keys())[:15]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_flyers_path())

