"""Test script to check selectors on kaufda.de"""
import asyncio
from playwright.async_api import async_playwright

async def test_selectors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading kaufda.de...")
        try:
            await page.goto("https://www.kaufda.de", wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(10000)  # Wait for dynamic content
        except Exception as e:
            print(f"Warning: Page load timeout or error: {e}")
            # Try to continue anyway
            pass
        
        print("\n=== Testing Flyer Selectors ===")
        # Test different selectors for flyers
        flyer_selectors = [
            'a[href*="/prospekt/"]',
            'a[href*="/prospekte/"]',
            'a[href*="prospekt"]',
            'article a[href*="prospekt"]',
            '[data-flyer]',
            '.flyer-item',
            '[class*="flyer"]',
            '[class*="prospekt"]',
        ]
        
        for selector in flyer_selectors:
            elements = await page.query_selector_all(selector)
            print(f"{selector}: {len(elements)} elements found")
            if elements:
                # Show first few hrefs
                for i, el in enumerate(elements[:3]):
                    href = await el.get_attribute('href')
                    text = await el.inner_text()
                    print(f"  [{i+1}] {href[:80] if href else 'N/A'} - {text[:50] if text else 'N/A'}")
        
        print("\n=== Testing Offer Selectors ===")
        offer_selectors = [
            "article",
            "[class*='offer']",
            "[class*='product']",
            ".offer-card",
            ".product-card",
            "[data-product]",
            '[class*="angebot"]',
            '[class*="Angebot"]',
        ]
        
        for selector in offer_selectors:
            elements = await page.query_selector_all(selector)
            print(f"{selector}: {len(elements)} elements found")
            if elements and len(elements) <= 10:
                for i, el in enumerate(elements[:3]):
                    text = await el.inner_text()
                    print(f"  [{i+1}] {text[:100] if text else 'N/A'}")
        
        print("\n=== Testing Retailer Selectors ===")
        retailer_selectors = [
            ".retailer-item",
            ".brand-item",
            "[class*='retailer']",
            "[class*='brand']",
            ".store-item",
            '[class*="händler"]',
            '[class*="Händler"]',
            'a[href*="/händler/"]',
            'a[href*="/haendler/"]',
        ]
        
        for selector in retailer_selectors:
            elements = await page.query_selector_all(selector)
            print(f"{selector}: {len(elements)} elements found")
            if elements and len(elements) <= 20:
                for i, el in enumerate(elements[:3]):
                    text = await el.inner_text()
                    href = await el.get_attribute('href')
                    print(f"  [{i+1}] {text[:50] if text else 'N/A'} - {href[:60] if href else 'N/A'}")
        
        print("\n=== Inspecting Offer Elements ===")
        offer_elements = await page.query_selector_all("[class*='offer']")
        if offer_elements:
            for i, el in enumerate(offer_elements[:5]):
                print(f"\nOffer Element {i+1}:")
                # Get all attributes
                attrs = await el.evaluate("el => Array.from(el.attributes).map(a => a.name + '=' + a.value)")
                print(f"  Attributes: {attrs[:3]}")
                # Get HTML structure
                html = await el.evaluate("el => el.outerHTML.substring(0, 200)")
                print(f"  HTML: {html}")
                # Get text content
                text = await el.inner_text()
                print(f"  Text: {text[:100] if text else 'N/A'}")
        
        print("\n=== Looking for Flyer Cards ===")
        # Try to find flyer cards by text content
        all_links = await page.query_selector_all("a")
        flyer_links = []
        for link in all_links:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            if text and ('prospekt' in text.lower() or 'seiten' in text.lower()):
                flyer_links.append((href, text[:80]))
        print(f"Found {len(flyer_links)} potential flyer links")
        for href, text in flyer_links[:5]:
            print(f"  {href[:60] if href else 'N/A'}: {text}")
        
        print("\n=== Looking for Product/Offer Cards ===")
        # Try different approaches
        cards = await page.query_selector_all("[class*='card'], [class*='item'], [class*='product'], [class*='offer']")
        print(f"Found {len(cards)} potential cards")
        for i, card in enumerate(cards[:5]):
            text = await card.inner_text()
            classes = await card.get_attribute('class')
            print(f"  Card {i+1}: class='{classes[:50] if classes else 'N/A'}' - text='{text[:60] if text else 'N/A'}'")
        
        print("\n=== Looking for Retailer Links ===")
        retailer_links = []
        for link in all_links[:100]:  # Check first 100 links
            text = await link.inner_text()
            href = await link.get_attribute('href')
            if href and ('/haendler/' in href or '/händler/' in href or '/retailer/' in href):
                retailer_links.append((href, text[:50] if text else ''))
        print(f"Found {len(retailer_links)} retailer links")
        for href, text in retailer_links[:5]:
            print(f"  {href}: {text}")
        
        # Save HTML to file for inspection
        html_content = await page.content()
        with open('kaufda_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("\n=== Saved page HTML to kaufda_page.html for inspection ===")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_selectors())

