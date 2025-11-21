"""Test extracting stores from a retailer detail page"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_retailer_stores():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Test with ALDI Nord
        retailer_url = "https://www.kaufda.de/Geschaefte/Aldi-Nord"
        print(f"Loading retailer page: {retailer_url}")
        
        try:
            await page.goto(retailer_url, wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(8000)  # Wait for dynamic content
            
            # Check page title
            title = await page.title()
            print(f"Page title: {title}")
            
            # Extract JSON
            retailer_json = await page.evaluate("""
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
            
            if not retailer_json:
                print("✗ No __NEXT_DATA__ JSON found")
                await browser.close()
                return
            
            print("✓ Found __NEXT_DATA__ JSON")
            
            # Save full JSON
            with open('retailer_aldi_nord_full.json', 'w', encoding='utf-8') as f:
                json.dump(retailer_json, f, indent=2, ensure_ascii=False)
            print("✓ Saved full JSON to retailer_aldi_nord_full.json")
            
            # Deep search for store data
            def find_stores(obj, path="", depth=0, max_depth=15):
                """Recursively search for store-like data"""
                if depth > max_depth:
                    return []
                
                stores_found = []
                
                if isinstance(obj, dict):
                    # Check for store-related keys
                    store_keys = ['stores', 'locations', 'branches', 'filialen', 'standorte', 'storeLocations', 'store_locations', 'storeLocationsList']
                    for key in store_keys:
                        if key in obj:
                            value = obj[key]
                            if isinstance(value, list) and len(value) > 0:
                                print(f"  ✓ Found '{key}' at path: {path}")
                                stores_found.append((path, key, value))
                    
                    # Check for store-like objects
                    if isinstance(obj, dict):
                        store_fields = ['address', 'city', 'postalCode', 'street', 'postcode', 'latitude', 'longitude', 'phone', 'openingHours']
                        found_fields = [k for k in store_fields if k in obj]
                        if len(found_fields) >= 3:  # At least 3 store fields
                            print(f"  ✓ Found store-like object at path: {path} (fields: {found_fields})")
                            stores_found.append((path, "store_object", obj))
                    
                    # Recursively search
                    for k, v in obj.items():
                        stores_found.extend(find_stores(v, f"{path}.{k}" if path else k, depth+1, max_depth))
                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        stores_found.extend(find_stores(item, f"{path}[{i}]", depth+1, max_depth))
                
                return stores_found
            
            stores_found = find_stores(retailer_json)
            
            if stores_found:
                print(f"\n✓ Found {len(stores_found)} potential store locations in JSON")
                for path, key, data in stores_found[:10]:
                    print(f"\n  Path: {path}, Key: {key}")
                    if isinstance(data, list) and len(data) > 0:
                        first_item = data[0]
                        if isinstance(first_item, dict):
                            print(f"    List length: {len(data)}")
                            print(f"    First item keys: {list(first_item.keys())[:15]}")
                            # Show sample data
                            sample = {k: first_item.get(k) for k in ['address', 'city', 'postalCode', 'street', 'postcode', 'latitude', 'longitude', 'phone', 'openingHours', 'name', 'title'] if k in first_item}
                            if sample:
                                print(f"    Sample data: {json.dumps(sample, indent=6, ensure_ascii=False)}")
                    elif isinstance(data, dict):
                        print(f"    Keys: {list(data.keys())[:15]}")
                        sample = {k: data.get(k) for k in ['address', 'city', 'postalCode', 'street', 'postcode', 'latitude', 'longitude', 'phone', 'openingHours', 'name', 'title'] if k in data}
                        if sample:
                            print(f"    Sample data: {json.dumps(sample, indent=6, ensure_ascii=False)}")
            else:
                print("✗ No store data found in JSON")
            
            # Check HTML for store information
            print("\n=== Checking HTML for store elements ===")
            store_elements = await page.query_selector_all('[class*="store"], [class*="location"], [class*="branch"], [class*="filiale"], [data-store], [data-location], [class*="standort"]')
            print(f"Found {len(store_elements)} store-related HTML elements")
            
            # Check for text containing store information
            page_text = await page.inner_text('body')
            if 'Filiale' in page_text or 'Standort' in page_text or 'Adresse' in page_text:
                print("✓ Page contains store-related text")
            
            # Look for store list or map
            store_list = await page.query_selector('[class*="store-list"], [class*="location-list"], [class*="filialen-list"]')
            if store_list:
                print("✓ Found store list element")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        await browser.close()
        print("\n=== Test completed ===")

if __name__ == "__main__":
    asyncio.run(test_retailer_stores())

