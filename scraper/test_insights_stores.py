"""Test insights page for stores"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_insights_stores():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "https://www.kaufda.de/insights/wo-gibt-es-aldi-nord-hier-findet-ihr-die-filialen/"
        print(f"Loading: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(10000)
        
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
                    store_fields = ['address', 'city', 'postalCode', 'street', 'postcode', 'latitude', 'longitude']
                    found_fields = [k for k in store_fields if k in obj]
                    if len(found_fields) >= 2:
                        stores.append((path, obj))
                    
                    for key in ['stores', 'locations', 'branches', 'filialen', 'standorte']:
                        if key in obj and isinstance(obj[key], list):
                            for i, item in enumerate(obj[key]):
                                if isinstance(item, dict):
                                    stores.extend(find_stores(item, f"{path}.{key}[{i}]", depth+1, max_depth))
                    
                    for k, v in obj.items():
                        stores.extend(find_stores(v, f"{path}.{k}" if path else k, depth+1, max_depth))
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        stores.extend(find_stores(item, f"{path}[{i}]", depth+1, max_depth))
                return stores
            
            stores = find_stores(json_data)
            if stores:
                print(f"✓ Found {len(stores)} stores in JSON")
                for path, store in stores[:10]:
                    print(f"  {path}: {store.get('address', 'N/A')}, {store.get('city', 'N/A')}, {store.get('postalCode', 'N/A')}")
            else:
                print("✗ No stores found in JSON")
        
        # Check HTML for store information
        body_text = await page.inner_text('body')
        if 'Filiale' in body_text or 'Standort' in body_text or 'Adresse' in body_text:
            print("\n✓ Page contains store-related text")
            # Look for addresses in text
            lines = body_text.split('\n')
            address_lines = []
            for line in lines:
                # Look for patterns like "Street, City PostalCode" or similar
                if any(char.isdigit() for char in line) and len(line) > 10:
                    address_lines.append(line.strip())
            
            if address_lines:
                print(f"\nFound {len(address_lines)} potential address lines:")
                for line in address_lines[:20]:
                    print(f"  {line[:100]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_insights_stores())

