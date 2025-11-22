# Off-Board Scraper

Python Scrapy-based scraper for extracting flyers, offers, and retailer data from kaufDA.de

## Features

- Scrapes flyers with page images and thumbnails
- Extracts offers with detailed product information
- Collects retailer and store data
- Stores data in PostgreSQL database
- Uses Playwright for JavaScript-rendered content

## Docker Usage

### Build Image

```bash
docker build -t off-board-scraper:latest ./scraper
```

### Run Container

```bash
docker run --rm \
  -e DATABASE_URL="postgresql://user:pass@host:5432/dbname" \
  -e SCRAPER_DELAY_MS=2000 \
  -e SCRAPER_RETRY_ATTEMPTS=3 \
  -e SCRAPER_TIMEOUT_MS=30000 \
  -e SCRAPER_HEADLESS=true \
  -e LOG_LEVEL=info \
  off-board-scraper:latest
```

### Using GitHub Container Registry

```bash
# Pull image
docker pull ghcr.io/mehran282/off-board-scraper:latest

# Run with environment variables
docker run --rm \
  -e DATABASE_URL="your-database-url" \
  ghcr.io/mehran282/off-board-scraper:latest
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (required)
- `SCRAPER_DELAY_MS`: Delay between requests in milliseconds (default: 2000)
- `SCRAPER_RETRY_ATTEMPTS`: Number of retry attempts (default: 3)
- `SCRAPER_TIMEOUT_MS`: Request timeout in milliseconds (default: 30000)
- `SCRAPER_HEADLESS`: Run browser in headless mode (default: true)
- `LOG_LEVEL`: Logging level (default: info)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set environment variables
cp .env.example .env
# Edit .env with your database URL

# Run scraper
python scripts/scrape_all.py
```

## Project Structure

```
scraper/
├── config/          # Configuration settings
├── database/        # Database connection and session
├── models/          # SQLAlchemy models
├── scraper/         # Scrapy project
│   ├── spiders/     # Spider implementations
│   ├── pipelines/   # Data processing pipelines
│   └── items.py     # Item definitions
├── scripts/         # CLI scripts
├── utils/           # Utility functions
└── scrapy.cfg       # Scrapy configuration
```

