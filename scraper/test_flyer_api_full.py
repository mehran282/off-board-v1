"""Test full flyer API extraction with pages and offers"""
import json
import requests

content_id = '6a2cd8bc-e4ea-4c3b-9949-8969d25842c0'
base_url = 'https://content-viewer-be.kaufda.de/api/v1'

# Try different API endpoints
endpoints = [
    f'/brochures/{content_id}?partner=kaufda_web&brochureKey=&lat=52.522&lng=13.4161',
    f'/brochures/{content_id}/pages?partner=kaufda_web&lat=52.522&lng=13.4161',
    f'/brochures/{content_id}/offers?partner=kaufda_web&lat=52.522&lng=13.4161',
    f'/brochures/{content_id}/content?partner=kaufda_web&lat=52.522&lng=13.4161',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

for endpoint in endpoints:
    url = base_url + endpoint
    print(f'\n=== Trying: {endpoint} ===')
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f'Status: {response.status_code}')
            print(f'Response keys: {list(data.keys())[:10]}')
            
            # Check for pages
            if 'pages' in data:
                pages = data['pages']
                print(f'Found {len(pages)} pages')
                if pages and isinstance(pages, list):
                    print(f'First page keys: {list(pages[0].keys())[:10]}')
            
            # Check for offers
            if 'offers' in data:
                offers = data['offers']
                print(f'Found {len(offers)} offers')
                if offers and isinstance(offers, list):
                    print(f'First offer keys: {list(offers[0].keys())[:15]}')
            
            # Save if interesting
            if 'pages' in data or 'offers' in data:
                filename = f'sample_{endpoint.replace("/", "_").replace("?", "_")}.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                print(f'Saved to {filename}')
        else:
            print(f'Status: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')

