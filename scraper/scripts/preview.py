"""Script to generate website preview screenshot"""
import sys
import os
import json
import base64
from playwright.sync_api import sync_playwright

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Generate preview screenshot"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = context.new_page()
            
            page.goto("https://www.kaufda.de", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            screenshot = page.screenshot(type="png", full_page=False)
            browser.close()
            
            # Convert bytes to base64
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8') if isinstance(screenshot, bytes) else str(screenshot)
            
            result = {
                "success": True,
                "screenshot": screenshot_b64,
            }
            print(json.dumps(result))
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
        }
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
