"""Analyze JSON structure to find retailer links and store data"""
import asyncio
import json
from playwright.async_api import async_playwright

async def analyze_json():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading kaufda.de...")
        await page.goto("https://www.kaufda.de", wait_until="domcontentloaded", timeout=90000)
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
        
        if not json_data:
            print("ERROR: Could not find __NEXT_DATA__")
            await browser.close()
            return
        
        # Save full JSON
        with open('main_page_full.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print("✓ Saved full JSON to main_page_full.json")
        
        # Analyze structure
        def print_structure(obj, path="", max_depth=5, current_depth=0):
            """Print structure of JSON"""
            if current_depth >= max_depth:
                return
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        print(f"{'  ' * current_depth}{key}: {type(value).__name__}")
                        print_structure(value, current_path, max_depth, current_depth + 1)
                    else:
                        if key in ['href', 'url', 'link', 'name', 'title']:
                            print(f"{'  ' * current_depth}{key}: {str(value)[:100]}")
            elif isinstance(obj, list) and len(obj) > 0:
                print(f"{'  ' * current_depth}List[{len(obj)}]")
                if len(obj) > 0:
                    print_structure(obj[0], f"{path}[0]", max_depth, current_depth + 1)
        
        print("\n=== JSON Structure ===")
        print_structure(json_data, max_depth=6)
        
        # Look for retailer links
        print("\n=== Searching for retailer links ===")
        def find_links(obj, path="", depth=0, max_depth=10):
            links = []
            if depth > max_depth:
                return links
            
            if isinstance(obj, dict):
                # Check for link-like keys
                for key in ['href', 'url', 'link', 'link_url', 'linkUrl']:
                    if key in obj:
                        value = obj[key]
                        if isinstance(value, str) and ('geschaeft' in value.lower() or 'haendler' in value.lower() or 'retailer' in value.lower() or '/Geschaefte/' in value):
                            links.append((path, key, value))
                
                # Check for retailer/publisher names with links
                if 'link_text' in obj or 'name' in obj:
                    name = obj.get('link_text') or obj.get('name')
                    href = obj.get('href') or obj.get('url') or obj.get('link')
                    if name and href:
                        links.append((path, 'retailer_link', {'name': name, 'href': href}))
                
                # Recursively search
                for k, v in obj.items():
                    links.extend(find_links(v, f"{path}.{k}" if path else k, depth+1, max_depth))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    links.extend(find_links(item, f"{path}[{i}]", depth+1, max_depth))
            
            return links
        
        links = find_links(json_data)
        print(f"Found {len(links)} potential retailer links")
        for path, key, value in links[:20]:
            print(f"  {path}.{key}: {value}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_json())

