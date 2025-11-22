"""Test flyer API extraction"""
import json
import requests

content_id = '6a2cd8bc-e4ea-4c3b-9949-8969d25842c0'
api_url = f'https://content-viewer-be.kaufda.de/api/v1/brochures/{content_id}?partner=kaufda_web&brochureKey=&lat=52.522&lng=13.4161'

print(f'Fetching from API: {api_url}\n')

response = requests.get(api_url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

if response.status_code == 200:
    data = response.json()
    
    print('=== API Response Keys ===')
    print(list(data.keys())[:20])
    
    # Brochure info
    print('\n=== Brochure Info ===')
    print('Title:', data.get('title'))
    print('Content ID:', data.get('contentId') or data.get('id'))
    print('Page Count:', data.get('pageCount') or len(data.get('pages', [])))
    
    # Pages (images)
    pages = data.get('pages', [])
    print(f'\n=== Pages (Images) ===')
    print(f'Number of pages: {len(pages)}')
    if pages:
        print('\n=== First 3 Pages ===')
        for i, page_data in enumerate(pages[:3]):
            print(f'\nPage {i+1}:')
            print('  Keys:', list(page_data.keys())[:10])
            if 'url' in page_data:
                url_data = page_data['url']
                if isinstance(url_data, dict):
                    print(f'  Large: {url_data.get("large")}')
                    print(f'  Normal: {url_data.get("normal")}')
                    print(f'  Thumbnail: {url_data.get("thumbnail")}')
                elif isinstance(url_data, str):
                    print(f'  URL: {url_data}')
            if 'page' in page_data:
                print(f'  Page Number: {page_data.get("page")}')
    
    # Offers
    offers = data.get('offers', [])
    print(f'\n=== Offers ===')
    print(f'Number of offers: {len(offers)}')
    if offers:
        print('\n=== First 3 Offers ===')
        for i, offer in enumerate(offers[:3]):
            print(f'\nOffer {i+1}:')
            print('  Keys:', list(offer.keys())[:15])
            print('  Title:', offer.get('title'))
            print('  Brand:', offer.get('brand'))
            prices = offer.get('prices', {})
            print('  Price:', prices.get('mainPrice'), prices.get('mainPriceFormatted'))
            print('  Old Price:', prices.get('secondaryPrice'), prices.get('secondaryPriceFormatted'))
            
            # Image
            offer_images = offer.get('offerImages', {})
            if offer_images:
                img_url = offer_images.get('url', {})
                if isinstance(img_url, dict):
                    print('  Image Large:', img_url.get('large'))
                elif isinstance(img_url, str):
                    print('  Image URL:', img_url)
            
            # Page number
            parent_content = offer.get('parentContent', {})
            if parent_content:
                page_info = parent_content.get('page', {})
                if page_info:
                    print('  Page Number:', page_info.get('number'))
    
    # Save sample data
    with open('sample_flyer_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print('\n=== Saved sample data to sample_flyer_data.json ===')
    
else:
    print(f'Error: {response.status_code}')
    print(response.text[:500])

