"""Test Store extraction from kaufda.de retailer pages"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_store_extraction():
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
        
        # Find retailer names
        retailers = []
        page_props = json_data.get("props", {}).get("pageProps", {})
        page_info = page_props.get("pageInformation", {})
        template_content = page_info.get("template", {}).get("content", {})
        
        # Extract from PublisherLinkbox
        publisher_linkbox = template_content.get("PublisherLinkbox", {}) or page_props.get("PublisherLinkbox", {})
        publisher_links = publisher_linkbox.get("links", [])
        
        for link in publisher_links[:5]:  # Test first 5 retailers
            name = link.get("link_text", "").strip()
            if name:
                retailers.append(name)
        
        print(f"\n=== Found {len(retailers)} retailers to test ===")
        for name in retailers:
            print(f"  - {name}")
        
        # Test first retailer detail page
        if retailers:
            retailer_name = retailers[0]
            # Try different URL patterns
            url_patterns = [
                f"https://www.kaufda.de/Geschaefte/{retailer_name.replace(' ', '-')}",
                f"https://www.kaufda.de/Geschaefte/{retailer_name}",
                f"https://www.kaufda.de/haendler/{retailer_name.replace(' ', '-')}",
                f"https://www.kaufda.de/retailer/{retailer_name.replace(' ', '-')}",
            ]
            
            for url in url_patterns:
                print(f"\n=== Testing URL: {url} ===")
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
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
                        def find_stores(obj, path="", depth=0, max_depth=10):
                            """Recursively search for store-like data"""
                            if depth > max_depth:
                                return []
                            
                            stores_found = []
                            
                            if isinstance(obj, dict):
                                # Check for store-related keys
                                store_keys = ['stores', 'locations', 'branches', 'filialen', 'standorte']
                                for key in store_keys:
                                    if key in obj:
                                        value = obj[key]
                                        if isinstance(value, list) and len(value) > 0:
                                            print(f"  Found '{key}' at path: {path}")
                                            stores_found.append((path, key, value))
                                
                                # Check for store-like objects
                                if 'address' in obj or 'city' in obj or 'postalCode' in obj:
                                    print(f"  Found store-like object at path: {path}")
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
                            for path, key, data in stores_found[:5]:  # Show first 5
                                print(f"  Path: {path}, Key: {key}")
                                if isinstance(data, list) and len(data) > 0:
                                    print(f"    First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                                elif isinstance(data, dict):
                                    print(f"    Keys: {list(data.keys())}")
                        else:
                            print("✗ No store data found in JSON")
                        
                        # Also check HTML for store information
                        store_elements = await page.query_selector_all('[class*="store"], [class*="location"], [class*="branch"], [class*="filiale"], [data-store], [data-location]')
                        print(f"\nFound {len(store_elements)} store-related HTML elements")
                        
                        # Save full JSON for inspection
                        with open(f'retailer_{retailer_name.replace(" ", "_")}_json.json', 'w', encoding='utf-8') as f:
                            json.dump(retailer_json, f, indent=2, ensure_ascii=False)
                        print(f"✓ Saved full JSON to retailer_{retailer_name.replace(' ', '_')}_json.json")
                        
                        break  # Success, stop trying other URLs
                    else:
                        print("✗ No __NEXT_DATA__ JSON found")
                        
                except Exception as e:
                    print(f"✗ Error: {e}")
                    continue
        
        await browser.close()
        print("\n=== Test completed ===")

if __name__ == "__main__":
    asyncio.run(test_store_extraction())

