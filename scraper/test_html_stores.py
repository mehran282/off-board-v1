"""Test HTML for store links and information"""
import asyncio
from playwright.async_api import async_playwright

async def test_html_stores():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "https://www.kaufda.de/Geschaefte/Aldi-Nord"
        print(f"Loading: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(10000)
        
        # Get all links
        all_links = await page.query_selector_all('a')
        print(f"\n=== Found {len(all_links)} total links ===")
        
        store_related_links = []
        for link in all_links:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if href and text:
                href_lower = href.lower()
                text_lower = text.lower()
                if any(keyword in href_lower or keyword in text_lower for keyword in ['filiale', 'standort', 'store', 'location', 'adresse', 'geschäft']):
                    store_related_links.append((href, text[:100]))
        
        print(f"\n=== Found {len(store_related_links)} store-related links ===")
        for href, text in store_related_links[:20]:
            print(f"  {text[:50]}: {href}")
        
        # Get all text content and search for store-related text
        body_text = await page.inner_text('body')
        if 'Filiale' in body_text or 'Standort' in body_text:
            print("\n✓ Page contains store-related text")
            # Find context around store-related words
            lines = body_text.split('\n')
            store_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['filiale', 'standort', 'adresse', 'geschäft'])]
            if store_lines:
                print(f"\nFound {len(store_lines)} lines with store-related text:")
                for line in store_lines[:10]:
                    print(f"  {line[:100]}")
        
        # Check for buttons
        buttons = await page.query_selector_all('button')
        print(f"\n=== Found {len(buttons)} buttons ===")
        for button in buttons[:10]:
            text = await button.inner_text()
            if text and any(keyword in text.lower() for keyword in ['filiale', 'standort', 'store', 'location']):
                print(f"  Store-related button: {text[:50]}")
        
        # Save HTML for inspection
        html = await page.content()
        with open('retailer_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\n✓ Saved HTML to retailer_page.html")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_html_stores())

