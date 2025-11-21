"""Test if stores are on city pages"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_city_stores():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Try a city page with a retailer
        # Format: https://www.kaufda.de/Staedte/{city}/{retailer}
        test_urls = [
            "https://www.kaufda.de/Staedte/Berlin",
            "https://www.kaufda.de/Staedte/Muenchen",
            "https://www.kaufda.de/Geschaefte/Aldi-Nord/Filialen",
            "https://www.kaufda.de/Geschaefte/Aldi-Nord/Standorte",
        ]
        
        for url in test_urls:
            print(f"\n=== Testing URL: {url} ===")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(5000)
                
                title = await page.title()
                print(f"Page title: {title}")
                
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
                
                if json_data:
                    # Deep search for stores
                    def find_stores(obj, path="", depth=0, max_depth=15):
                        if depth > max_depth:
                            return []
                        stores = []
                        if isinstance(obj, dict):
                            # Check for store-like objects
                            store_fields = ['address', 'city', 'postalCode', 'street', 'postcode']
                            found_fields = [k for k in store_fields if k in obj]
                            if len(found_fields) >= 2:
                                stores.append((path, obj))
                            
                            # Check for store arrays
                            for key in ['stores', 'locations', 'branches', 'filialen', 'standorte']:
                                if key in obj and isinstance(obj[key], list):
                                    for i, item in enumerate(obj[key]):
                                        if isinstance(item, dict):
                                            stores.extend(find_stores(item, f"{path}.{key}[{i}]", depth+1, max_depth))
                            
                            # Recursively search
                            for k, v in obj.items():
                                stores.extend(find_stores(v, f"{path}.{k}" if path else k, depth+1, max_depth))
                        elif isinstance(obj, list):
                            for i, item in enumerate(obj):
                                stores.extend(find_stores(item, f"{path}[{i}]", depth+1, max_depth))
                        return stores
                    
                    stores = find_stores(json_data)
                    if stores:
                        print(f"✓ Found {len(stores)} stores in JSON")
                        for path, store in stores[:5]:
                            print(f"  {path}: {store.get('address', 'N/A')}, {store.get('city', 'N/A')}, {store.get('postalCode', 'N/A')}")
                    else:
                        print("✗ No stores found in JSON")
                else:
                    print("✗ No JSON found")
                
            except Exception as e:
                print(f"✗ Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_city_stores())

