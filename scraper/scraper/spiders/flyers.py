"""Flyer spider"""
import re
import json
import scrapy
from datetime import datetime, UTC
from scrapy_playwright.page import PageMethod
from scrapy.http import Request
from ..items import FlyerItem, OfferItem


class FlyersSpider(scrapy.Spider):
    """Spider for scraping flyers from kaufDA.de"""
    name = "flyers"
    allowed_domains = ["kaufda.de", "www.kaufda.de"]
    start_urls = ["https://www.kaufda.de"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://www.kaufda.de"

    def parse(self, response):
        """Parse main page and extract flyer data from JSON"""
        yield response.follow(
            response.url,
            callback=self.parse_flyer_list,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "domcontentloaded", timeout=60000),
                    PageMethod("wait_for_timeout", 5000),
                ],
            },
        )

    def parse_flyer_list(self, response):
        """Extract flyer data from embedded JSON"""
        # Extract JSON data from __NEXT_DATA__ script tag
        json_data = None
        script_tags = response.css('script#__NEXT_DATA__::text').getall()
        
        if not script_tags:
            # Try alternative selector
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
            return self.parse_flyer_list_html(response)
        
        # Extract flyers from JSON
        try:
            page_props = json_data.get("props", {}).get("pageProps", {})
            # Try pageInformation first, then fallback to direct
            page_info = page_props.get("pageInformation", {})
            brochures = page_info.get("brochures", {}) or page_props.get("brochures", {})
            
            # Flyers are in topRanked, not main.items
            top_ranked = brochures.get("topRanked", [])
            main_brochures = brochures.get("main", {}).get("items", [])
            all_brochures = top_ranked + main_brochures  # Combine both sources
            
            self.logger.info(f"Found {len(all_brochures)} flyers in JSON (topRanked: {len(top_ranked)}, main: {len(main_brochures)})")
            
            for brochure in all_brochures:
                item = FlyerItem()
                
                # Extract basic info
                item["title"] = brochure.get("title", "")
                item["url"] = f"{self.base_url}/Prospekte/{brochure.get('id', '')}"
                content_id = brochure.get("contentId")
                item["contentId"] = content_id
                if content_id:
                    self.logger.debug(f"Extracted contentId: {content_id} for {item['title']}")
                
                # Extract retailer name
                publisher = brochure.get("publisher", {})
                retailer_name = publisher.get("name", "")
                item["retailerId"] = retailer_name
                
                # Extract pages
                item["pages"] = brochure.get("pageCount", 0)
                
                # Extract published dates
                published_from_str = brochure.get("publishedFrom")
                published_until_str = brochure.get("publishedUntil")
                
                if published_from_str:
                    try:
                        item["publishedFrom"] = datetime.fromisoformat(published_from_str.replace("+0000", "+00:00"))
                    except (ValueError, AttributeError):
                        pass
                
                if published_until_str:
                    try:
                        item["publishedUntil"] = datetime.fromisoformat(published_until_str.replace("+0000", "+00:00"))
                    except (ValueError, AttributeError):
                        pass
                
                # Extract dates
                valid_from_str = brochure.get("validFrom")
                valid_until_str = brochure.get("validUntil")
                
                if valid_from_str:
                    try:
                        # Parse ISO format: 2025-11-16T23:00:00.000+0000
                        item["validFrom"] = datetime.fromisoformat(valid_from_str.replace("+0000", "+00:00"))
                    except (ValueError, AttributeError):
                        item["validFrom"] = datetime.now(UTC)
                else:
                    item["validFrom"] = datetime.now(UTC)
                
                if valid_until_str:
                    try:
                        item["validUntil"] = datetime.fromisoformat(valid_until_str.replace("+0000", "+00:00"))
                    except (ValueError, AttributeError):
                        item["validUntil"] = datetime.now(UTC)
                else:
                    item["validUntil"] = datetime.now(UTC)
                
                # Extract preview image (thumbnail) - در JSON جدید، thumbnail در pages[0].url است
                # اول سعی می‌کنیم از pages[0].url استفاده کنیم
                pages = brochure.get("pages", [])
                if pages and len(pages) > 0:
                    first_page = pages[0]
                    if isinstance(first_page, dict):
                        page_url = first_page.get("url", {})
                        if isinstance(page_url, dict):
                            # Try different sizes - large is best quality for thumbnail
                            thumbnail_url = (
                                page_url.get("large") or 
                                page_url.get("normal") or 
                                page_url.get("thumbnail") or
                                page_url.get("url")
                            )
                            if thumbnail_url:
                                item["thumbnailUrl"] = thumbnail_url
                                self.logger.debug(f"Extracted thumbnailUrl from pages[0].url: {thumbnail_url}")
                        elif isinstance(page_url, str):
                            item["thumbnailUrl"] = page_url
                            self.logger.debug(f"Extracted thumbnailUrl from pages[0].url (string): {page_url}")
                
                # If still no thumbnail, try to get from preview image URL pattern
                if not item.get("thumbnailUrl") and content_id:
                    # Build preview URL from contentId
                    preview_url = f"https://content-media.bonial.biz/{content_id}/preview.jpg"
                    item["thumbnailUrl"] = preview_url
                    self.logger.debug(f"Built thumbnailUrl from contentId: {preview_url}")
                
                # Fallback: Check preview field (for older JSON structure)
                if not item.get("thumbnailUrl"):
                    preview = brochure.get("preview", {})
                    if preview:
                        preview_url = preview.get("url", {})
                        if isinstance(preview_url, dict):
                            thumbnail_url = (
                                preview_url.get("large") or 
                                preview_url.get("normal") or 
                                preview_url.get("thumbnail") or
                                preview_url.get("url")
                            )
                            if thumbnail_url:
                                item["thumbnailUrl"] = thumbnail_url
                        elif isinstance(preview_url, str):
                            item["thumbnailUrl"] = preview_url
                
                # Also check direct preview/image fields
                if not item.get("thumbnailUrl"):
                    image_url = brochure.get("imageUrl") or brochure.get("thumbnailUrl") or brochure.get("previewUrl")
                    if image_url:
                        if isinstance(image_url, dict):
                            item["thumbnailUrl"] = image_url.get("url") or image_url.get("large") or image_url.get("normal")
                        elif isinstance(image_url, str):
                            item["thumbnailUrl"] = image_url
                
                # اگر thumbnailUrl پیدا نشد، سعی کنیم از PDF URL بسازیم
                # معمولاً URL PDF به صورت https://content-media.bonial.biz/{id}/file.pdf است
                # و preview به صورت https://content-media.bonial.biz/{id}/preview.jpg است
                if not item.get("thumbnailUrl") and item.get("pdfUrl"):
                    pdf_url = item["pdfUrl"]
                    # اگر URL شامل bonial.biz است، preview.jpg را بسازیم
                    if "bonial.biz" in pdf_url:
                        # جایگزین کردن /file.pdf با /preview.jpg
                        if "/file.pdf" in pdf_url:
                            preview_url = pdf_url.replace("/file.pdf", "/preview.jpg")
                        elif pdf_url.endswith(".pdf"):
                            preview_url = pdf_url.replace(".pdf", "/preview.jpg")
                        else:
                            # اگر ساختار متفاوت است، سعی کنیم preview.jpg را اضافه کنیم
                            preview_url = pdf_url.rstrip("/") + "/preview.jpg"
                        item["thumbnailUrl"] = preview_url
                
                # Extract PDF URL - flyers don't have PDF, they have images
                # So we don't set pdfUrl, but we'll fetch pages from API later
                # pdf_url = brochure.get("downloadUrl") or brochure.get("pdfUrl")
                # if pdf_url:
                #     item["pdfUrl"] = pdf_url
                
                # Always fetch thumbnail from pages API if we have contentId
                # This ensures we get the first page image as thumbnail
                if content_id:
                    # Request pages API to get first page image as thumbnail
                    pages_api_url = f"https://content-viewer-be.kaufda.de/api/v1/brochures/{content_id}/pages?partner=kaufda_web&lat=52.522&lng=13.4161"
                    yield Request(
                        pages_api_url,
                        callback=self.parse_flyer_thumbnail,
                        meta={
                            "flyer_item": item,
                            "content_id": content_id,
                        },
                        dont_filter=True,
                        priority=1,  # Higher priority to get thumbnail first
                    )
                else:
                    # Yield flyer item if no contentId
                    yield item
                
                # Also fetch pages API to get offers (separate request)
                if content_id:
                    pages_api_url = f"https://content-viewer-be.kaufda.de/api/v1/brochures/{content_id}/pages?partner=kaufda_web&lat=52.522&lng=13.4161"
                    yield Request(
                        pages_api_url,
                        callback=self.parse_flyer_pages,
                        meta={
                            "flyer_item": item,
                            "content_id": content_id,
                        },
                        dont_filter=True,
                    )
                
        except Exception as e:
            self.logger.error(f"Error parsing JSON flyer data: {e}")
            # Fallback to HTML parsing
            return self.parse_flyer_list_html(response)

    def parse_flyer_list_html(self, response):
        """Fallback: Extract flyer links from HTML"""
        flyer_selectors = [
            'a[href*="/prospekt/"]',
            'a[href*="/prospekte/"]',
            'a[href*="prospekt"]',
        ]

        flyer_links = []
        for selector in flyer_selectors:
            links = response.css(selector + "::attr(href)").getall()
            for link in links:
                if link and link not in flyer_links:
                    if link.startswith("/"):
                        link = self.base_url + link
                    elif not link.startswith("http"):
                        link = self.base_url + "/" + link
                    flyer_links.append(link)

        self.logger.info(f"Found {len(flyer_links)} flyer links in HTML")

        for link in flyer_links[:20]:
            yield Request(
                link,
                callback=self.parse_flyer_details,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded", timeout=60000),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                },
            )

    def parse_flyer_details(self, response):
        """Extract flyer details from detail page"""
        item = FlyerItem()

        # Extract title
        title = response.css("h1::text, h2::text, [class*='title']::text").get()
        if title:
            title = title.strip()
        else:
            title = response.css("title::text").get() or ""

        if not title or len(title) < 5:
            self.logger.warning(f"No title found for {response.url}")
            return

        item["title"] = title
        item["url"] = response.url

        # Extract retailer name from title
        retailer_name = None
        if "Prospekt" in title or "prospekt" in title:
            idx = title.lower().find("prospekt")
            retailer_name = title[:idx].strip()
        else:
            parts = title.split()
            retailer_name = parts[0] if parts else None

        # Extract pages
        body_text = response.css("body").get() or ""
        pages_match = re.search(r"(\d+)\s*(Seiten|seiten|pages)", body_text, re.IGNORECASE)
        pages = int(pages_match.group(1)) if pages_match else 1

        # Extract dates
        valid_from = datetime.now(UTC)
        valid_until = datetime.now(UTC)

        date_matches = re.findall(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", body_text)
        if len(date_matches) >= 2:
            try:
                day1, month1, year1 = date_matches[0]
                day2, month2, year2 = date_matches[1]
                valid_from = datetime(int(year1), int(month1), int(day1))
                valid_until = datetime(int(year2), int(month2), int(day2))
            except (ValueError, IndexError):
                pass

        item["pages"] = pages
        item["validFrom"] = valid_from
        item["validUntil"] = valid_until
        item["retailerId"] = retailer_name

        # Extract PDF URL
        pdf_url = response.css('a[href*=".pdf"]::attr(href)').get()
        if pdf_url:
            if pdf_url.startswith("/"):
                pdf_url = self.base_url + pdf_url
            item["pdfUrl"] = pdf_url

        yield item

    def parse_flyer_thumbnail(self, response):
        """Parse flyer pages API to extract first page image as thumbnail"""
        try:
            data = json.loads(response.text)
            contents = data.get("contents", [])
            flyer_item = response.meta.get("flyer_item", {})
            content_id = response.meta.get("content_id")
            
            # Extract thumbnail from first page (page 0)
            if contents:
                first_page = contents[0]
                images = first_page.get("images", [])
                if images:
                    # Use the largest image (usually last one) for best quality
                    # But for thumbnail, we can use a medium size (768x1024 or 1600x1600)
                    # Try to find a good balance between quality and size
                    thumbnail_url = None
                    for img in images:
                        size = img.get("size", "")
                        url = img.get("url")
                        # Prefer 768x1024 or 1600x1600 for thumbnail
                        if "768x1024" in size or "1600x1600" in size:
                            thumbnail_url = url
                            break
                    # If no medium size found, use largest
                    if not thumbnail_url:
                        thumbnail_url = images[-1].get("url") if images else None
                    
                    if thumbnail_url:
                        flyer_item["thumbnailUrl"] = thumbnail_url
                        self.logger.info(f"Extracted thumbnailUrl from pages API for {content_id}: {thumbnail_url[:80]}...")
            
            # Yield flyer item with thumbnail - this will update existing or create new
            yield flyer_item
            
        except Exception as e:
            self.logger.error(f"Error parsing flyer thumbnail from API: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            # Yield original item even if thumbnail extraction fails
            flyer_item = response.meta.get("flyer_item", {})
            yield flyer_item

    def parse_flyer_pages(self, response):
        """Parse flyer pages API response to extract page images and offers"""
        try:
            data = json.loads(response.text)
            contents = data.get("contents", [])
            flyer_item = response.meta.get("flyer_item", {})
            content_id = response.meta.get("content_id")
            
            self.logger.info(f"Found {len(contents)} pages for flyer {content_id}")
            
            # Note: thumbnailUrl should already be set from pages[0].url in parse_flyer_list
            # But if not, we can extract from pages API as fallback
            if contents:
                first_page = contents[0]
                images = first_page.get("images", [])
                if images and not flyer_item.get("thumbnailUrl"):
                    # Use the largest image (usually last one)
                    thumbnail_url = images[-1].get("url") if images else None
                    if thumbnail_url:
                        # Create a flyer update item to update thumbnailUrl
                        update_item = FlyerItem()
                        update_item["url"] = flyer_item.get("url")
                        update_item["thumbnailUrl"] = thumbnail_url
                        update_item["title"] = flyer_item.get("title")  # Required field
                        update_item["retailerId"] = flyer_item.get("retailerId")  # Required field
                        update_item["pages"] = flyer_item.get("pages", 0)  # Required field
                        update_item["validFrom"] = flyer_item.get("validFrom")  # Required field
                        update_item["validUntil"] = flyer_item.get("validUntil")  # Required field
                        self.logger.debug(f"Updating flyer with thumbnailUrl from pages API: {thumbnail_url}")
                        yield update_item
            
            # Extract offers from all pages
            for page_data in contents:
                page_number = page_data.get("number", 0)
                offers = page_data.get("offers", [])
                
                for offer_data in offers:
                    offer_content = offer_data.get("content", {})
                    if offer_content and offer_content.get("type") == "offer":
                        # Create offer item
                        offer_item = OfferItem()
                        
                        # Extract product info
                        products = offer_content.get("products", [])
                        if products:
                            product = products[0]
                            offer_item["productName"] = product.get("name", "")
                            offer_item["brand"] = product.get("brandName")
                            description_parts = product.get("description", [])
                            if description_parts:
                                offer_item["description"] = " ".join([d.get("paragraph", "") for d in description_parts if isinstance(d, dict)])
                        
                        # Extract price
                        deals = offer_content.get("deals", [])
                        if deals:
                            deal = deals[0]
                            offer_item["currentPrice"] = deal.get("min", 0.0) or deal.get("max", 0.0)
                            offer_item["priceFormatted"] = f"{offer_item['currentPrice']} {deal.get('currencyCode', 'EUR')}"
                            offer_item["priceFrequency"] = deal.get("frequency")
                            offer_item["unitPrice"] = deal.get("priceByBaseUnit")
                        
                        # Extract image
                        offer_item["imageUrl"] = offer_content.get("image")
                        
                        # Extract parent content info
                        parent_content = offer_content.get("parentContent", {})
                        if parent_content:
                            offer_item["parentContentId"] = parent_content.get("id")
                            page_info = parent_content.get("page", {})
                            if page_info:
                                offer_item["pageNumber"] = page_info.get("number")
                        
                        # Extract retailer
                        publisher = offer_content.get("publisher", {})
                        offer_item["retailerId"] = publisher.get("name", "")
                        offer_item["publisherId"] = publisher.get("id")
                        
                        # Extract offer ID and URL
                        offer_id = offer_content.get("id")
                        offer_item["contentId"] = offer_id
                        if offer_id:
                            offer_item["url"] = f"{self.base_url}/Angebote/{offer_id}"
                        
                        # Extract category from categoryPaths
                        category_paths = products[0].get("categoryPaths", []) if products else []
                        if category_paths:
                            # Use the most specific category (last one)
                            offer_item["category"] = category_paths[-1].get("name")
                        
                        yield offer_item
            
        except Exception as e:
            self.logger.error(f"Error parsing flyer pages API: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
