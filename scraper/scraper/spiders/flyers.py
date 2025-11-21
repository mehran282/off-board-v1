"""Flyer spider"""
import re
import json
import scrapy
from datetime import datetime, UTC
from scrapy_playwright.page import PageMethod
from scrapy.http import Request
from ..items import FlyerItem


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
                
                # Extract retailer name
                publisher = brochure.get("publisher", {})
                retailer_name = publisher.get("name", "")
                item["retailerId"] = retailer_name
                
                # Extract pages
                item["pages"] = brochure.get("pageCount", 0)
                
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
                
                # Extract preview image (thumbnail) - سایت خودش preview image دارد
                # معمولاً در preview.url.large یا preview.url.normal است
                preview = brochure.get("preview", {})
                if preview:
                    preview_url = preview.get("url", {})
                    if isinstance(preview_url, dict):
                        # Try different sizes
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
                
                # Extract PDF URL - باید URL صحیح PDF را پیدا کنیم
                # معمولاً در downloadUrl یا pdfUrl یا pages[0].url است
                pdf_url = brochure.get("downloadUrl") or brochure.get("pdfUrl")
                if pdf_url:
                    item["pdfUrl"] = pdf_url
                else:
                    # Fallback: از pages استخراج کنیم
                    pages = brochure.get("pages", [])
                    if pages and len(pages) > 0:
                        first_page = pages[0]
                        if isinstance(first_page, dict):
                            page_url = first_page.get("url", {})
                            if isinstance(page_url, dict):
                                # برای PDF، معمولاً large یا normal است
                                pdf_url = (
                                    page_url.get("large") or 
                                    page_url.get("normal") or 
                                    page_url.get("url")
                                )
                                if pdf_url and pdf_url.endswith('.pdf'):
                                    item["pdfUrl"] = pdf_url
                            elif isinstance(page_url, str) and page_url.endswith('.pdf'):
                                item["pdfUrl"] = page_url
                        elif isinstance(first_page, str) and first_page.endswith('.pdf'):
                            item["pdfUrl"] = first_page
                
                yield item
                
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
