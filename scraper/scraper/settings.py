"""Scrapy settings"""
import os
from dotenv import load_dotenv

load_dotenv()

# Scrapy settings
BOT_NAME = "kaufda_scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure delays
DOWNLOAD_DELAY = float(os.getenv("SCRAPER_DOWNLOAD_DELAY", "1"))
RANDOMIZE_DOWNLOAD_DELAY = True

# Concurrent requests
CONCURRENT_REQUESTS = int(os.getenv("SCRAPER_CONCURRENT_REQUESTS", "16"))
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# User agent
USER_AGENT = os.getenv(
    "SCRAPER_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Playwright settings (for JavaScript rendering)
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Use default reactor (compatible with Python 3.13)
# TWISTED_REACTOR = "twisted.internet.asyncio.AsyncIOReactor"

# Playwright browser settings
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 60000,  # 60 seconds timeout
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000  # 60 seconds

# Pipelines
ITEM_PIPELINES = {
    "scraper.pipelines.ValidationPipeline": 300,
    "scraper.pipelines.DeduplicationPipeline": 400,
    "scraper.pipelines.DatabasePipeline": 500,
    "scraper.pipelines.LoggingPipeline": 600,
}

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = None  # Set to a file path to log to file

