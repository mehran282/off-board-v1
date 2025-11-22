"""Offer spider"""
import re
import json
import scrapy
from datetime import datetime
from scrapy_playwright.page import PageMethod
from ..items import OfferItem


class OffersSpider(scrapy.Spider):
    """Spider for scraping offers from kaufDA.de"""
    name = "offers"
    allowed_domains = ["kaufda.de", "www.kaufda.de"]
    start_urls = ["https://www.kaufda.de"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://www.kaufda.de"

    def parse(self, response):
        """Parse main page and extract offer data from JSON"""
        yield response.follow(
            response.url,
            callback=self.parse_offers,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "domcontentloaded", timeout=60000),
                    PageMethod("wait_for_timeout", 5000),
                ],
            },
        )

    def parse_offers(self, response):
        """Extract offer data from embedded JSON"""
        # Extract JSON data from __NEXT_DATA__ script tag
        json_data = None
        script_tags = response.css('script#__NEXT_DATA__::text').getall()
        
        if not script_tags:
            script_tags = response.xpath('//script[@id="__NEXT_DATA__"]/text()').getall()
        
        for script_content in script_tags:
            try:
                json_data = json.loads(script_content)
                break
            except json.JSONDecodeError:
                continue
        
        if not json_data:
            self.logger.warning("Could not find __NEXT_DATA__ JSON")
            # Fallback to HTML parsing
            for item in self.parse_offers_html(response):
                yield item
            return
        
        # Extract offers from JSON
        try:
            page_props = json_data.get("props", {}).get("pageProps", {})
            # Try pageInformation first, then fallback to direct
            page_info = page_props.get("pageInformation", {})
            offers_data = page_info.get("offers", {}) or page_props.get("offers", {})
            main_offers = offers_data.get("main", {}).get("items", [])
            
            self.logger.info(f"Found {len(main_offers)} offers in JSON")
            
            for offer in main_offers:
                item = OfferItem()
                
                # Extract basic info
                item["productName"] = offer.get("title", "")
                item["brand"] = offer.get("brand")
                item["contentId"] = offer.get("id")
                item["publisherId"] = offer.get("publisherId")
                
                # Description might be in different places
                description = offer.get("description")
                if not description:
                    preview = offer.get("preview")
                    if isinstance(preview, dict):
                        description = preview.get("description")
                item["description"] = description
                
                # Extract parent content (flyer info)
                parent_content = offer.get("parentContent", {})
                if parent_content:
                    item["parentContentId"] = parent_content.get("id")
                    page_info = parent_content.get("page", {})
                    if page_info:
                        item["pageNumber"] = page_info.get("number")
                
                # Extract prices
                prices = offer.get("prices", {})
                item["currentPrice"] = prices.get("mainPrice", 0.0) or prices.get("price", 0.0) or 0.0
                item["priceFormatted"] = prices.get("mainPriceFormatted")
                item["priceFrequency"] = prices.get("mainPriceFrequency")
                
                # Extract price conditions
                conditions = prices.get("conditions", [])
                if conditions:
                    import json
                    item["priceConditions"] = json.dumps(conditions)
                
                # Extract unit price
                unit_price = prices.get("priceByBaseUnit")
                if unit_price:
                    item["unitPrice"] = unit_price
                
                # Try multiple fields for old price
                secondary_price = prices.get("secondaryPrice", 0.0)
                item["oldPriceFormatted"] = prices.get("secondaryPriceFormatted")
                
                # Set oldPrice if secondary_price exists and is greater than currentPrice
                if secondary_price and secondary_price > 0 and secondary_price > item["currentPrice"]:
                    item["oldPrice"] = secondary_price
                    # Calculate discount
                    discount = secondary_price - item["currentPrice"]
                    item["discount"] = discount
                    item["discountPercentage"] = (discount / secondary_price) * 100
                
                # Extract dates
                valid_from_str = offer.get("validFrom")
                valid_until_str = offer.get("validUntil")
                
                if valid_from_str:
                    try:
                        item["validFrom"] = datetime.fromisoformat(valid_from_str.replace("+0000", "+00:00"))
                    except (ValueError, AttributeError):
                        pass
                
                if valid_until_str:
                    try:
                        item["validUntil"] = datetime.fromisoformat(valid_until_str.replace("+0000", "+00:00"))
                    except (ValueError, AttributeError):
                        pass
                
                # Extract image URL and metadata
                offer_images = offer.get("offerImages", {})
                image_url = offer_images.get("url", {})
                if image_url:
                    item["imageUrl"] = image_url.get("large") or image_url.get("normal") or image_url.get("thumbnail")
                
                # Extract image metadata
                image_metadata = offer_images.get("metaData", {})
                if image_metadata:
                    item["imageAlt"] = image_metadata.get("imageAlt")
                    item["imageTitle"] = image_metadata.get("imageTitle")
                
                # Extract retailer
                retailer_name = offer.get("publisherName", "")
                item["retailerId"] = retailer_name
                
                # Extract URL (construct from offer ID)
                offer_id = offer.get("id", "")
                if offer_id:
                    item["url"] = f"{self.base_url}/Angebote/{offer_id}"
                else:
                    item["url"] = response.url
                
                # Extract category (if available)
                parent_content = offer.get("parentContent", {})
                item["category"] = parent_content.get("type")
                
                yield item
                
        except Exception as e:
            self.logger.error(f"Error parsing JSON offer data: {e}")
            # Fallback to HTML parsing
            for item in self.parse_offers_html(response):
                yield item

    def parse_offers_html(self, response):
        """Fallback: Extract offers from HTML"""
        # Try to find offer elements
        offer_elements = response.css("[class*='offerItem'], [class*='offer']")
        
        self.logger.info(f"Found {len(offer_elements)} offer elements in HTML")
        
        for element in offer_elements[:50]:
            item = OfferItem()
            
            # Extract from img alt/title attributes
            img_selector = element.css("img")
            if img_selector:
                alt_text = img_selector.css("::attr(alt)").get() or ""
                title_text = img_selector.css("::attr(title)").get() or ""
                
                # Parse alt text: "Wodka Original bei REWE im Prospekt für 6,49 €"
                if alt_text:
                    # Extract product name (before "bei")
                    if " bei " in alt_text:
                        product_name = alt_text.split(" bei ")[0].strip()
                        item["productName"] = product_name
                    
                    # Extract retailer (after "bei" and before "im")
                    if " bei " in alt_text and " im " in alt_text:
                        retailer_part = alt_text.split(" bei ")[1].split(" im ")[0].strip()
                        item["retailerId"] = retailer_part
                    
                    # Extract price
                    price_match = re.search(r"(\d+[,.]?\d*)\s*€", alt_text)
                    if price_match:
                        price_str = price_match.group(1).replace(",", ".")
                        try:
                            item["currentPrice"] = float(price_str)
                        except ValueError:
                            continue
                
                # Extract image URL
                img_src = img_selector.css("::attr(src)").get()
                if img_src:
                    if img_src.startswith("/"):
                        img_src = self.base_url + img_src
                    elif not img_src.startswith("http"):
                        img_src = self.base_url + "/" + img_src
                    item["imageUrl"] = img_src
            
            if "productName" not in item or not item["productName"]:
                continue
            
            item["url"] = response.url
            yield item
