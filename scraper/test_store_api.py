"""Test if stores are loaded via API calls"""
import asyncio
from playwright.async_api import async_playwright

async def test_store_api():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Listen to network requests
        api_calls = []
        
        async def handle_response(response):
            url = response.url
            # Check for store/location related API calls
            if any(keyword in url.lower() for keyword in ['store', 'location', 'filiale', 'standort', 'branch', 'api']):
                try:
                    body = await response.body()
                    api_calls.append({
                        'url': url,
                        'status': response.status,
                        'method': response.request.method,
                        'body': body[:1000] if len(body) < 1000 else body[:1000] + b'...',
                    })
                except:
                    pass
        
        page.on('response', handle_response)
        
        print("Loading retailer page: https://www.kaufda.de/Geschaefte/Aldi-Nord")
        await page.goto("https://www.kaufda.de/Geschaefte/Aldi-Nord", wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(10000)  # Wait for all API calls
        
        print(f"\n=== Found {len(api_calls)} potential store-related API calls ===")
        for i, call in enumerate(api_calls[:20], 1):
            print(f"\n{i}. {call['method']} {call['url']}")
            print(f"   Status: {call['status']}")
            if call['body']:
                try:
                    body_str = call['body'].decode('utf-8', errors='ignore')
                    if len(body_str) > 200:
                        body_str = body_str[:200] + "..."
                    print(f"   Body preview: {body_str}")
                except:
                    print(f"   Body: {call['body'][:100]}")
        
        # Also check for store-related elements in the page
        print("\n=== Checking for store-related elements ===")
        store_elements = await page.query_selector_all('[class*="store"], [class*="location"], [class*="filiale"], [data-store], [data-location]')
        print(f"Found {len(store_elements)} store-related HTML elements")
        
        # Check for buttons/links that might load stores
        store_buttons = await page.query_selector_all('button[class*="store"], a[href*="Filiale"], a[href*="Standort"]')
        print(f"Found {len(store_buttons)} store-related buttons/links")
        
        # Try clicking on store-related buttons if any
        if store_buttons:
            print("\n=== Trying to click store-related buttons ===")
            for i, button in enumerate(store_buttons[:3]):
                try:
                    text = await button.inner_text()
                    print(f"Clicking button {i+1}: {text[:50]}")
                    await button.click()
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"Error clicking button: {e}")
        
        # Check for store data in page after interactions
        await page.wait_for_timeout(5000)
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
                    if 'address' in obj and 'city' in obj:
                        stores.append((path, obj))
                    for k, v in obj.items():
                        stores.extend(find_stores(v, f"{path}.{k}" if path else k, depth+1, max_depth))
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        stores.extend(find_stores(item, f"{path}[{i}]", depth+1, max_depth))
                return stores
            
            stores = find_stores(json_data)
            if stores:
                print(f"\n✓ Found {len(stores)} stores in JSON after interactions")
                for path, store in stores[:5]:
                    print(f"  {path}: {store.get('address', 'N/A')}, {store.get('city', 'N/A')}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_store_api())

