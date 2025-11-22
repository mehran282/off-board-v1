"""Test thumbnail extraction"""
import json
from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page()
page.goto('https://www.kaufda.de', wait_until='domcontentloaded', timeout=60000)
page.wait_for_timeout(5000)
script = page.query_selector('script#__NEXT_DATA__')
data = json.loads(script.inner_text()) if script else {}
brochures = data.get('props', {}).get('pageProps', {}).get('pageInformation', {}).get('brochures', {})
top_ranked = brochures.get('topRanked', [])

if top_ranked:
    flyer = top_ranked[0]
    print('Flyer title:', flyer.get('title'))
    print('Has preview:', 'preview' in flyer and flyer.get('preview') is not None)
    print('Has pages:', 'pages' in flyer and len(flyer.get('pages', [])) > 0)
    
    if flyer.get('pages') and len(flyer.get('pages', [])) > 0:
        first_page = flyer['pages'][0]
        print('First page keys:', list(first_page.keys()))
        if 'url' in first_page:
            page_url = first_page['url']
            print('Page URL type:', type(page_url))
            if isinstance(page_url, dict):
                print('Page URL keys:', list(page_url.keys()))
                print('Page URL large:', page_url.get('large'))
                print('Page URL normal:', page_url.get('normal'))
                print('Page URL thumbnail:', page_url.get('thumbnail'))

browser.close()
p.stop()

