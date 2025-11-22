"""Test flyer detail URL extraction"""
import json
import requests
from playwright.sync_api import sync_playwright

url = 'https://www.kaufda.de/contentViewer/static/1edb6208-ad12-4255-9664-7cdc870109e9?adFormat=ad_format__brochure_card_cover&adPlacement=ad_placement__shelf_sort_managed&feature=brochure_shelf&lat=52.522&lng=13.4161&pageType=SHELF_PAGE&retailerName=EURONICS&sourceValue=EURONICS&sourceType=PORTAL_WIDGET&visitOriginType=WEB_REFERRER_SEO&zip=10178&page=1'

# Extract contentId from URL
content_id = '1edb6208-ad12-4255-9664-7cdc870109e9'

print(f'Content ID: {content_id}\n')

# Try API endpoint
api_url = f'https://content-viewer-be.kaufda.de/api/v1/brochures/{content_id}/pages?partner=kaufda_web&lat=52.522&lng=13.4161'

print(f'Fetching from API: {api_url}\n')
response = requests.get(api_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

if response.status_code == 200:
    data = response.json()
    contents = data.get('contents', [])
    
    print(f'Found {len(contents)} pages\n')
    
    if contents:
        first_page = contents[0]
        print('=== First Page (Page 0) ===')
        print('Keys:', list(first_page.keys()))
        
        images = first_page.get('images', [])
        print(f'\nNumber of images: {len(images)}')
        
        if images:
            print('\n=== All Images ===')
            for i, img in enumerate(images):
                print(f'Image {i+1}:')
                print(f'  Size: {img.get("size")}')
                print(f'  URL: {img.get("url")}')
            
            # Use largest image (last one)
            thumbnail_url = images[-1].get('url')
            print(f'\n=== Selected Thumbnail (largest) ===')
            print(f'URL: {thumbnail_url}')
        else:
            print('No images found in first page')
    else:
        print('No pages found')
else:
    print(f'API Error: {response.status_code}')
    print(response.text[:500])

