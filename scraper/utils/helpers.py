"""Helper functions"""
import re
from datetime import datetime
from typing import Optional


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime"""
    if not date_str:
        return None

    # Try common date formats
    formats = [
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    # Try regex pattern
    match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", date_str)
    if match:
        day, month, year = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except ValueError:
            pass

    return None


def extract_price(price_str: str) -> Optional[float]:
    """Extract price from string"""
    if not price_str:
        return None

    # Remove currency symbols and whitespace
    price_str = re.sub(r"[€$£]", "", price_str).strip()

    # Replace comma with dot
    price_str = price_str.replace(",", ".")

    # Extract number
    match = re.search(r"(\d+\.?\d*)", price_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    return None


def normalize_url(url: str, base_url: str = "https://www.kaufda.de") -> str:
    """Normalize URL"""
    if not url:
        return base_url

    if url.startswith("http"):
        return url
    elif url.startswith("/"):
        return base_url + url
    else:
        return base_url + "/" + url

