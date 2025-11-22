"""Analyze pages API response"""
import json
import requests

content_id = '6a2cd8bc-e4ea-4c3b-9949-8969d25842c0'
url = f'https://content-viewer-be.kaufda.de/api/v1/brochures/{content_id}/pages?partner=kaufda_web&lat=52.522&lng=13.4161'

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

if response.status_code == 200:
    data = response.json()
    print('=== Pages API Response ===')
    print('Keys:', list(data.keys()))
    
    contents = data.get('contents', [])
    print(f'\nNumber of contents: {len(contents)}')
    
    if contents:
        print('\n=== First Content ===')
        first = contents[0]
        print('Keys:', list(first.keys())[:20])
        print('\nFull first content:')
        print(json.dumps(first, indent=2, ensure_ascii=False)[:2000])
        
        print('\n=== Sample Contents (first 3) ===')
        for i, content in enumerate(contents[:3]):
            print(f'\nContent {i+1}:')
            print('  Type:', content.get('type'))
            print('  Page:', content.get('page'))
            if 'url' in content:
                url_data = content['url']
                if isinstance(url_data, dict):
                    print('  URL large:', url_data.get('large'))
                    print('  URL normal:', url_data.get('normal'))
                elif isinstance(url_data, str):
                    print('  URL:', url_data)
            
            # Check for offers in content
            if 'offers' in content:
                offers = content['offers']
                print(f'  Offers: {len(offers)}')
                if offers:
                    print('  First offer:', offers[0].get('title') if isinstance(offers[0], dict) else offers[0])
    
    # Save for analysis
    with open('pages_api_response.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print('\n=== Saved to pages_api_response.json ===')

