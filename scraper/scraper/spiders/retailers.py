"""Retailer spider"""
import json
import scrapy
from scrapy_playwright.page import PageMethod
from ..items import RetailerItem, StoreItem


class RetailersSpider(scrapy.Spider):
    """Spider for scraping retailers from kaufDA.de"""
    name = "retailers"
    allowed_domains = ["kaufda.de", "www.kaufda.de"]
    start_urls = ["https://www.kaufda.de"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://www.kaufda.de"

    def parse(self, response):
        """Parse main page and extract retailer data from JSON"""
        yield response.follow(
            response.url,
            callback=self.parse_retailers,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "domcontentloaded", timeout=60000),
                    PageMethod("wait_for_timeout", 5000),
                ],
            },
        )

    def parse_retailers(self, response):
        """Extract retailer data from embedded JSON"""
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
            return self.parse_retailers_html(response)
        
        retailers = []
        seen_names = set()
        
        try:
            page_props = json_data.get("props", {}).get("pageProps", {})
            page_info = page_props.get("pageInformation", {})
            template_content = page_info.get("template", {}).get("content", {})
            
            # Extract from PublisherLinkbox (in template.content)
            publisher_linkbox = template_content.get("PublisherLinkbox", {}) or page_props.get("PublisherLinkbox", {})
            publisher_links = publisher_linkbox.get("links", [])
            
            for link in publisher_links:
                name = link.get("link_text", "").strip()
                if name and name not in seen_names:
                    item = RetailerItem()
                    item["name"] = name
                    item["category"] = "General"  # Default category
                    
                    # Extract logo URL if available
                    logo_url = link.get("image_url")
                    if logo_url:
                        item["logoUrl"] = logo_url
                    
                    retailers.append(item)
                    seen_names.add(name)
            
            # Extract from PublisherLogoLinkbox (in template.content)
            publisher_logo_linkbox = template_content.get("PublisherLogoLinkbox_Other", {}) or page_props.get("PublisherLogoLinkbox_Other", {})
            publisher_logo_links = publisher_logo_linkbox.get("links", [])
            
            for link in publisher_logo_links:
                name = link.get("link_text", "").strip()
                if not name:
                    # Try image_metaTitle or description
                    name = link.get("image_metaTitle", "").replace(" Prospekte & Angebote", "").strip()
                    if not name:
                        name = link.get("description", "").strip()
                
                if name and name not in seen_names:
                    item = RetailerItem()
                    item["name"] = name
                    item["category"] = "General"
                    
                    logo_url = link.get("image_url")
                    if logo_url:
                        item["logoUrl"] = logo_url
                    
                    retailers.append(item)
                    seen_names.add(name)
            
            # Extract from flyers (publishers)
            brochures = page_info.get("brochures", {}) or page_props.get("brochures", {})
            main_brochures = brochures.get("main", {}).get("items", [])
            
            for brochure in main_brochures:
                publisher = brochure.get("publisher", {})
                name = publisher.get("name", "").strip()
                
                if name and name not in seen_names:
                    item = RetailerItem()
                    item["name"] = name
                    item["category"] = "General"
                    
                    logo = publisher.get("logo", {})
                    logo_url_obj = logo.get("url", {})
                    if logo_url_obj:
                        item["logoUrl"] = logo_url_obj.get("large") or logo_url_obj.get("normal")
                    
                    retailers.append(item)
                    seen_names.add(name)
            
            # Extract from offers (publishers)
            offers_data = page_info.get("offers", {}) or page_props.get("offers", {})
            main_offers = offers_data.get("main", {}).get("items", [])
            
            for offer in main_offers:
                retailer_name = offer.get("publisherName", "").strip()
                
                if retailer_name and retailer_name not in seen_names:
                    item = RetailerItem()
                    item["name"] = retailer_name
                    item["category"] = "General"
                    retailers.append(item)
                    seen_names.add(retailer_name)
            
            self.logger.info(f"Found {len(retailers)} retailers in JSON")
            
            # Yield retailers and schedule store scraping
            for item in retailers:
                yield item
                # Schedule retailer detail page to get stores
                retailer_name = item.get("name")
                if retailer_name:
                    # Try multiple URL patterns for retailer pages
                    retailer_slug = retailer_name.replace(' ', '-').replace('ü', 'ue').replace('ö', 'oe').replace('ä', 'ae').replace('ß', 'ss')
                    url_patterns = [
                        f"{self.base_url}/Geschaefte/{retailer_slug}",
                        f"{self.base_url}/Geschaefte/{retailer_name.replace(' ', '-')}",
                        f"{self.base_url}/{retailer_slug}",
                    ]
                    
                    # Also check if there's a direct link in the JSON
                    # Check PublisherLinkbox links
                    for link in publisher_links:
                        if link.get("link_text", "").strip() == retailer_name:
                            href = link.get("link_href", "")
                            if href:
                                if href.startswith("http"):
                                    url_patterns.insert(0, href)
                                elif href.startswith("/"):
                                    # Extract retailer slug from href (e.g., /Aldi-Nord/Sortiment -> /Geschaefte/Aldi-Nord)
                                    if "/Sortiment" in href:
                                        retailer_slug_from_href = href.replace("/Sortiment", "").replace("/", "")
                                        url_patterns.insert(0, f"{self.base_url}/Geschaefte/{retailer_slug_from_href}")
                                    else:
                                        url_patterns.insert(0, f"{self.base_url}{href}")
                    
                    # Also check PublisherLogoLinkbox links
                    for link in publisher_logo_links:
                        link_text = link.get("link_text", "").strip()
                        if not link_text:
                            link_text = link.get("image_metaTitle", "").replace(" Prospekte & Angebote", "").strip()
                        if link_text == retailer_name:
                            href = link.get("link_href", "") or link.get("href", "")
                            if href:
                                if href.startswith("http"):
                                    url_patterns.insert(0, href)
                                elif href.startswith("/"):
                                    if "/Sortiment" in href:
                                        retailer_slug_from_href = href.replace("/Sortiment", "").replace("/", "")
                                        url_patterns.insert(0, f"{self.base_url}/Geschaefte/{retailer_slug_from_href}")
                                    else:
                                        url_patterns.insert(0, f"{self.base_url}{href}")
                    
                    # Try first URL pattern
                    if url_patterns:
                        yield response.follow(
                            url_patterns[0],
                            callback=self.parse_retailer_stores,
                            meta={
                                "playwright": True,
                                "playwright_page_methods": [
                                    PageMethod("wait_for_load_state", "domcontentloaded", timeout=60000),
                                    PageMethod("wait_for_timeout", 5000),
                                ],
                                "retailer_name": retailer_name,
                                "retailer_id": item.get("id"),  # If available
                                "alternative_urls": url_patterns[1:],  # Try alternatives if first fails
                            },
                            errback=self.errback_retailer_stores,
                        )
            
            # Try to extract stores from JSON (if available on main page)
            stores = self._extract_stores_from_json(json_data, seen_names)
            for store_item in stores:
                yield store_item
                
        except Exception as e:
            self.logger.error(f"Error parsing JSON retailer data: {e}")
            return self.parse_retailers_html(response)
    
    def _extract_stores_from_json(self, json_data: dict, retailer_names: set):
        """Extract store data from JSON if available"""
        stores = []
        
        try:
            page_props = json_data.get("props", {}).get("pageProps", {})
            page_info = page_props.get("pageInformation", {})
            
            # Check if stores are available in the JSON structure
            # This is a placeholder - actual structure may vary
            # Stores might be in publisher data or a separate stores section
            
            # Try to find stores in publisher data
            brochures = page_info.get("brochures", {}) or page_props.get("brochures", {})
            main_brochures = brochures.get("main", {}).get("items", [])
            
            for brochure in main_brochures:
                publisher = brochure.get("publisher", {})
                retailer_name = publisher.get("name", "").strip()
                
                # Check if publisher has store information
                # This structure may need to be adjusted based on actual JSON
                stores_data = publisher.get("stores", [])
                if not stores_data:
                    # Try alternative paths
                    stores_data = publisher.get("locations", [])
                    stores_data = publisher.get("branches", [])
                
                for store_data in stores_data:
                    if isinstance(store_data, dict):
                        store_item = StoreItem()
                        store_item["retailerId"] = retailer_name
                        store_item["address"] = store_data.get("address", "")
                        store_item["city"] = store_data.get("city", "")
                        store_item["postalCode"] = store_data.get("postalCode", "") or store_data.get("postcode", "")
                        store_item["latitude"] = store_data.get("latitude")
                        store_item["longitude"] = store_data.get("longitude")
                        store_item["phone"] = store_data.get("phone", "")
                        
                        # Handle opening hours (convert to JSON string if dict/list)
                        opening_hours = store_data.get("openingHours") or store_data.get("opening_hours")
                        if opening_hours:
                            if isinstance(opening_hours, (dict, list)):
                                import json as json_lib
                                store_item["openingHours"] = json_lib.dumps(opening_hours)
                            else:
                                store_item["openingHours"] = str(opening_hours)
                        
                        if store_item["address"]:
                            stores.append(store_item)
            
            self.logger.info(f"Found {len(stores)} stores in JSON")
            
        except Exception as e:
            self.logger.warning(f"Error extracting stores from JSON: {e}")
        
        return stores

    def parse_retailers_html(self, response):
        """Fallback: Extract retailers from HTML"""
        retailers = []
        seen_names = set()
        
        # Try to find retailer links
        retailer_links = response.css('a[href*="/Geschaefte/"], a[href*="/Sortiment"]')
        
        for link in retailer_links:
            text = link.css("::text").get()
            href = link.css("::attr(href)").get()
            
            if text:
                name = text.strip()
                if name and name not in seen_names and len(name) > 2:
                    item = RetailerItem()
                    item["name"] = name
                    item["category"] = "General"
                    
                    # Try to extract logo
                    img = link.css("img").first
                    if img:
                        logo_url = img.css("::attr(src)").get()
                        if logo_url:
                            if logo_url.startswith("/"):
                                logo_url = self.base_url + logo_url
                            elif not logo_url.startswith("http"):
                                logo_url = self.base_url + "/" + logo_url
                            item["logoUrl"] = logo_url
                    
                    retailers.append(item)
                    seen_names.add(name)
        
        self.logger.info(f"Found {len(retailers)} retailers in HTML")
        
        for item in retailers:
            yield item
    
    def parse_retailer_stores(self, response):
        """Parse retailer detail page to extract stores"""
        retailer_name = response.meta.get("retailer_name")
        if not retailer_name:
            return
        
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
            self.logger.warning(f"Could not find __NEXT_DATA__ JSON for retailer {retailer_name}")
            # Try alternative URLs if available
            alternative_urls = response.meta.get("alternative_urls", [])
            if alternative_urls:
                next_url = alternative_urls[0]
                self.logger.info(f"Trying alternative URL for {retailer_name}: {next_url}")
                yield response.follow(
                    next_url,
                    callback=self.parse_retailer_stores,
                    meta={
                        **response.meta,
                        "alternative_urls": alternative_urls[1:],
                    },
                    errback=self.errback_retailer_stores,
                )
            return
        
        # Extract stores from JSON
        stores = self._extract_stores_from_retailer_json(json_data, retailer_name)
        
        # Also check for store links in HTML and follow them
        store_links = response.css('a[href*="Filiale"], a[href*="Standort"], a[href*="store"], a[href*="location"]::attr(href)').getall()
        for link in store_links[:10]:  # Limit to first 10 store links
            if link:
                full_url = response.urljoin(link)
                yield response.follow(
                    full_url,
                    callback=self.parse_store_page,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "domcontentloaded", timeout=60000),
                            PageMethod("wait_for_timeout", 3000),
                        ],
                        "retailer_name": retailer_name,
                    },
                )
        
        for store_item in stores:
            yield store_item
    
    def _extract_stores_from_retailer_json(self, json_data: dict, retailer_name: str):
        """Extract store data from retailer detail page JSON - deep search"""
        stores = []
        
        try:
            # Deep recursive search for store data
            def find_store_objects(obj, path="", depth=0, max_depth=20):
                """Recursively find store-like objects"""
                if depth > max_depth:
                    return []
                
                found_stores = []
                
                if isinstance(obj, dict):
                    # Check if this is a store-like object
                    store_fields = ['address', 'city', 'postalCode', 'street', 'postcode', 'zipCode']
                    found_fields = [k for k in store_fields if k in obj]
                    
                    if len(found_fields) >= 2:  # At least 2 store fields
                        found_stores.append(obj)
                    
                    # Check for store-related keys
                    store_keys = ['stores', 'locations', 'branches', 'filialen', 'standorte', 'storeLocations', 'store_locations']
                    for key in store_keys:
                        if key in obj:
                            value = obj[key]
                            if isinstance(value, list):
                                for item in value:
                                    if isinstance(item, dict):
                                        found_stores.extend(find_store_objects(item, f"{path}.{key}", depth+1, max_depth))
                    
                    # Recursively search
                    for k, v in obj.items():
                        found_stores.extend(find_store_objects(v, f"{path}.{k}" if path else k, depth+1, max_depth))
                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        found_stores.extend(find_store_objects(item, f"{path}[{i}]", depth+1, max_depth))
                
                return found_stores
            
            all_store_objects = find_store_objects(json_data)
            
            # Convert found objects to StoreItems
            seen_stores = set()
            for store_data in all_store_objects:
                if not isinstance(store_data, dict):
                    continue
                
                address = store_data.get("address", "") or store_data.get("street", "") or store_data.get("streetAddress", "")
                city = store_data.get("city", "") or store_data.get("cityName", "")
                postal_code = str(store_data.get("postalCode", "") or store_data.get("postcode", "") or store_data.get("zipCode", "") or store_data.get("zip", ""))
                
                # Skip if missing essential fields
                if not address or not city:
                    continue
                
                # Create unique key to avoid duplicates
                store_key = f"{retailer_name}:{address}:{city}:{postal_code}"
                if store_key in seen_stores:
                    continue
                seen_stores.add(store_key)
                
                store_item = StoreItem()
                store_item["retailerId"] = retailer_name
                store_item["address"] = address
                store_item["city"] = city
                store_item["postalCode"] = postal_code
                store_item["latitude"] = store_data.get("latitude") or store_data.get("lat") or store_data.get("geoLatitude")
                store_item["longitude"] = store_data.get("longitude") or store_data.get("lng") or store_data.get("lon") or store_data.get("geoLongitude")
                store_item["phone"] = store_data.get("phone", "") or store_data.get("telephone", "") or store_data.get("phoneNumber", "")
                
                # Handle opening hours
                opening_hours = (
                    store_data.get("openingHours") or 
                    store_data.get("opening_hours") or 
                    store_data.get("hours") or
                    store_data.get("openingTimes")
                )
                if opening_hours:
                    if isinstance(opening_hours, (dict, list)):
                        import json as json_lib
                        store_item["openingHours"] = json_lib.dumps(opening_hours, ensure_ascii=False)
                    else:
                        store_item["openingHours"] = str(opening_hours)
                
                stores.append(store_item)
            
            self.logger.info(f"Found {len(stores)} stores for retailer {retailer_name}")
            
        except Exception as e:
            self.logger.warning(f"Error extracting stores for retailer {retailer_name}: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
        
        return stores
    
    def parse_store_page(self, response):
        """Parse individual store page"""
        retailer_name = response.meta.get("retailer_name")
        if not retailer_name:
            return
        
        # Extract JSON from store page
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
        
        if json_data:
            stores = self._extract_stores_from_retailer_json(json_data, retailer_name)
            for store_item in stores:
                yield store_item
    
    def errback_retailer_stores(self, failure):
        """Handle errors when fetching retailer stores"""
        retailer_name = failure.request.meta.get("retailer_name", "unknown")
        self.logger.warning(f"Failed to fetch stores for retailer {retailer_name}: {failure.value}")
