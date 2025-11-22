"""Test flyer detail page extraction"""
import json
from playwright.sync_api import sync_playwright

url = 'https://www.kaufda.de/contentViewer/static/6a2cd8bc-e4ea-4c3b-9949-8969d25842c0?adFormat=ad_format__brochure_card_cover&adPlacement=ad_placement__shelf_fixed_position_2&feature=brochure_shelf&lat=52.522&lng=13.4161&pageType=SHELF_PAGE&retailerName=REWE&sourceValue=REWE&sourceType=PORTAL_WIDGET&visitOriginType=WEB_REFERRER_SEO&zip=10178&page=8&locality=Berlin'

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page()

# Listen for network requests
api_responses = []
def handle_response(response):
    if 'api' in response.url.lower() or 'contentViewer' in response.url.lower() or 'brochure' in response.url.lower():
        api_responses.append({
            'url': response.url,
            'status': response.status,
            'headers': dict(response.headers)
        })

page.on('response', handle_response)

page.goto(url, wait_until='domcontentloaded', timeout=60000)
page.wait_for_timeout(5000)

print('=== API Responses ===')
for resp in api_responses[:10]:
    print(f"URL: {resp['url']}")
    print(f"Status: {resp['status']}")
    print()

# Try to get JSON data
script = page.query_selector('script#__NEXT_DATA__')
if script:
    data = json.loads(script.inner_text())
    print('=== __NEXT_DATA__ Structure ===')
    print('Top level keys:', list(data.keys())[:10])
    
    props = data.get('props', {})
    print('Props keys:', list(props.keys())[:10])
    
    page_props = props.get('pageProps', {})
    print('PageProps keys:', list(page_props.keys())[:10])
    
    page_info = page_props.get('pageInformation', {})
    print('PageInformation keys:', list(page_info.keys())[:15])
    
    # Try different paths
    brochure = page_info.get('brochure') or page_info.get('brochures') or page_props.get('brochure')
    if brochure:
        print('\n=== Found Brochure ===')
        print('Brochure keys:', list(brochure.keys())[:20])
    else:
        print('\n=== No brochure found, checking all keys ===')
        print('All page_info keys:', list(page_info.keys()))
        print('All page_props keys:', list(page_props.keys()))

# Try to get page images
images = page.query_selector_all('img[src*="content-media.bonial.biz"]')
print(f'\n=== Found {len(images)} images ===')
for i, img in enumerate(images[:5]):
    src = img.get_attribute('src')
    print(f'Image {i+1}: {src}')

browser.close()
p.stop()
