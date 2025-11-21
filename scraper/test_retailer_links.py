"""Test extracting retailer links and finding store pages"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_retailer_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Loading kaufda.de main page...")
        try:
            await page.goto("https://www.kaufda.de", wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"Warning: {e}")
        
        # Extract JSON from main page
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
        
        # Extract retailer links from JSON
        retailers_with_links = []
        page_props = json_data.get("props", {}).get("pageProps", {})
        page_info = page_props.get("pageInformation", {})
        template_content = page_info.get("template", {}).get("content", {})
        
        # Extract from PublisherLinkbox
        publisher_linkbox = template_content.get("PublisherLinkbox", {}) or page_props.get("PublisherLinkbox", {})
        publisher_links = publisher_linkbox.get("links", [])
        
        for link in publisher_links[:10]:  # Test first 10 retailers
            name = link.get("link_text", "").strip()
            href = link.get("href", "") or link.get("url", "")
            
            if name and href:
                retailers_with_links.append({
                    "name": name,
                    "href": href,
                    "full_url": href if href.startswith("http") else f"https://www.kaufda.de{href}"
                })
        
        print(f"\n=== Found {len(retailers_with_links)} retailers with links ===")
        for retailer in retailers_with_links[:5]:
            print(f"  {retailer['name']}: {retailer['full_url']}")
        
        # Test first retailer page
        if retailers_with_links:
            retailer = retailers_with_links[0]
            print(f"\n=== Testing retailer page: {retailer['name']} ===")
            print(f"URL: {retailer['full_url']}")
            
            try:
                await page.goto(retailer['full_url'], wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(5000)
                
                # Check if page loaded successfully
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
                
                if retailer_json:
                    print("✓ Found __NEXT_DATA__ JSON")
                    
                    # Deep search for store data
                    def find_stores(obj, path="", depth=0, max_depth=15):
                        """Recursively search for store-like data"""
                        if depth > max_depth:
                            return []
                        
                        stores_found = []
                        
                        if isinstance(obj, dict):
                            # Check for store-related keys
                            store_keys = ['stores', 'locations', 'branches', 'filialen', 'standorte', 'storeLocations', 'store_locations']
                            for key in store_keys:
                                if key in obj:
                                    value = obj[key]
                                    if isinstance(value, list) and len(value) > 0:
                                        print(f"  ✓ Found '{key}' at path: {path}")
                                        stores_found.append((path, key, value))
                            
                            # Check for store-like objects (has address, city, postalCode)
                            if isinstance(obj, dict) and any(k in obj for k in ['address', 'city', 'postalCode', 'street', 'postcode']):
                                # Make sure it's not just a single field
                                store_fields = ['address', 'city', 'postalCode', 'street', 'postcode', 'latitude', 'longitude', 'phone']
                                if sum(1 for k in store_fields if k in obj) >= 2:
                                    print(f"  ✓ Found store-like object at path: {path}")
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
                        for path, key, data in stores_found[:10]:  # Show first 10
                            print(f"\n  Path: {path}, Key: {key}")
                            if isinstance(data, list) and len(data) > 0:
                                first_item = data[0]
                                if isinstance(first_item, dict):
                                    print(f"    List length: {len(data)}")
                                    print(f"    First item keys: {list(first_item.keys())[:10]}")
                                    # Show sample data
                                    sample = {k: first_item.get(k) for k in ['address', 'city', 'postalCode', 'street', 'postcode', 'latitude', 'longitude', 'phone'] if k in first_item}
                                    if sample:
                                        print(f"    Sample data: {sample}")
                            elif isinstance(data, dict):
                                print(f"    Keys: {list(data.keys())[:15]}")
                                sample = {k: data.get(k) for k in ['address', 'city', 'postalCode', 'street', 'postcode', 'latitude', 'longitude', 'phone'] if k in data}
                                if sample:
                                    print(f"    Sample data: {sample}")
                    else:
                        print("✗ No store data found in JSON")
                    
                    # Also check HTML for store links or buttons
                    store_links = await page.query_selector_all('a[href*="store"], a[href*="location"], a[href*="filiale"], a[href*="standort"], button[class*="store"], button[class*="location"]')
                    print(f"\nFound {len(store_links)} store-related links/buttons in HTML")
                    
                    # Check for "Filialen" or "Standorte" links
                    all_links = await page.query_selector_all('a')
                    store_page_links = []
                    for link in all_links:
                        href = await link.get_attribute('href')
                        text = await link.inner_text()
                        if href and text:
                            text_lower = text.lower()
                            if any(word in text_lower for word in ['filiale', 'standort', 'store', 'location', 'geschäft', 'adresse']):
                                store_page_links.append((href, text[:50]))
                    
                    if store_page_links:
                        print(f"\nFound {len(store_page_links)} potential store page links:")
                        for href, text in store_page_links[:5]:
                            print(f"  {text}: {href}")
                    
                    # Save full JSON for inspection
                    with open(f'retailer_{retailer["name"].replace(" ", "_")}_full.json', 'w', encoding='utf-8') as f:
                        json.dump(retailer_json, f, indent=2, ensure_ascii=False)
                    print(f"\n✓ Saved full JSON to retailer_{retailer['name'].replace(' ', '_')}_full.json")
                    
                else:
                    print("✗ No __NEXT_DATA__ JSON found")
                    
            except Exception as e:
                print(f"✗ Error: {e}")
                import traceback
                traceback.print_exc()
        
        await browser.close()
        print("\n=== Test completed ===")

if __name__ == "__main__":
    asyncio.run(test_retailer_links())

