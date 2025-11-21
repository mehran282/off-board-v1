"""Application settings"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Scraper settings
SCRAPER_USER_AGENT = os.getenv(
    "SCRAPER_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SCRAPER_DOWNLOAD_DELAY = float(os.getenv("SCRAPER_DOWNLOAD_DELAY", "1"))
SCRAPER_CONCURRENT_REQUESTS = int(os.getenv("SCRAPER_CONCURRENT_REQUESTS", "16"))

