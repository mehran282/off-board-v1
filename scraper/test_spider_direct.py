"""Test spider directly"""
import sys
import os
import json

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings
from scraper.spiders.flyers import FlyersSpider
from scraper.spiders.offers import OffersSpider
from scraper.spiders.retailers import RetailersSpider

# Create a mock response with JSON data
html_content = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "pageInformation": {
        "brochures": {
          "main": {
            "items": [
              {
                "title": "REWE Prospekt Test",
                "publisher": {
                  "name": "REWE",
                  "logo": {
                    "url": {
                      "large": "https://example.com/logo.png"
                    }
                  }
                },
                "pageCount": 22,
                "validFrom": "2025-11-16T23:00:00.000+0000",
                "validUntil": "2025-11-22T22:00:00.000+0000",
                "pages": [{
                  "url": {
                    "large": "https://example.com/flyer.pdf"
                  }
                }]
              }
            ]
          }
        },
        "offers": {
          "main": {
            "items": [
              {
                "title": "Test Product",
                "brand": "Test Brand",
                "publisherName": "REWE",
                "prices": {
                  "mainPrice": 6.49,
                  "secondaryPrice": 8.99
                },
                "validFrom": "2025-11-16T23:00:00.000+0000",
                "validUntil": "2025-11-22T22:00:00.000+0000",
                "offerImages": {
                  "url": {
                    "large": "https://example.com/image.jpg"
                  }
                },
                "id": "test-offer-123"
              }
            ]
          }
        },
        "template": {
          "content": {
            "PublisherLinkbox": {
              "links": [
                {
                  "link_text": "REWE",
                  "image_url": "https://example.com/logo.png"
                }
              ]
            }
          }
        }
      }
    }
  }
}
</script>
</body>
</html>
"""

response = HtmlResponse(url="https://www.kaufda.de", body=html_content.encode('utf-8'))

print("=== Testing FlyersSpider ===")
flyer_spider = FlyersSpider()
items = list(flyer_spider.parse_flyer_list(response))
print(f"Found {len(items)} flyer items")
for item in items:
    print(f"  - {item.get('title', 'N/A')} ({item.get('pages', 0)} pages)")

print("\n=== Testing OffersSpider ===")
offer_spider = OffersSpider()
items = list(offer_spider.parse_offers(response))
print(f"Found {len(items)} offer items")
for item in items:
    print(f"  - {item.get('productName', 'N/A')} - {item.get('currentPrice', 0)} €")

print("\n=== Testing RetailersSpider ===")
retailer_spider = RetailersSpider()
items = list(retailer_spider.parse_retailers(response))
print(f"Found {len(items)} retailer items")
for item in items:
    print(f"  - {item.get('name', 'N/A')}")

