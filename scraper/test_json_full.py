"""Test full JSON structure"""
import asyncio
import json
from playwright.async_api import async_playwright

async def test_json_full():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading kaufda.de...")
        try:
            await page.goto("https://www.kaufda.de", wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(15000)
        except Exception as e:
            print(f"Warning: {e}")
        
        # Get full JSON
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
        
        # Search for brochures/offers in the entire JSON
        def find_keys(obj, target_keys, path=""):
            """Recursively find keys in JSON"""
            results = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if any(tk in key.lower() for tk in target_keys):
                        results.append((current_path, type(value).__name__, len(value) if isinstance(value, (list, dict)) else 'N/A'))
                    if isinstance(value, (dict, list)):
                        results.extend(find_keys(value, target_keys, current_path))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    results.extend(find_keys(item, target_keys, f"{path}[{i}]"))
            return results
        
        print("\n=== Searching for 'brochure' related keys ===")
        brochure_results = find_keys(json_data, ['brochure', 'prospekt'])
        for path, type_name, length in brochure_results[:10]:
            print(f"  {path}: {type_name} ({length})")
        
        print("\n=== Searching for 'offer' related keys ===")
        offer_results = find_keys(json_data, ['offer', 'angebot'])
        for path, type_name, length in offer_results[:10]:
            print(f"  {path}: {type_name} ({length})")
        
        print("\n=== Searching for 'publisher' related keys ===")
        publisher_results = find_keys(json_data, ['publisher', 'retailer', 'haendler'])
        for path, type_name, length in publisher_results[:10]:
            print(f"  {path}: {type_name} ({length})")
        
        # Try to get the actual data
        print("\n=== Trying to access data directly ===")
        try:
            # Try the path we saw in HTML
            props = json_data.get("props", {})
            page_props = props.get("pageProps", {})
            
            # Check if data is in a different location
            if "brochures" not in page_props:
                # Maybe it's in the buildId or query?
                print("Checking alternative locations...")
                query = props.get("query", {})
                print(f"Query keys: {list(query.keys())[:10]}")
                
        except Exception as e:
            print(f"Error accessing data: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_json_full())

