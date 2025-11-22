# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers
RUN pip install --no-cache-dir playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper code
COPY scrapy.cfg .
COPY config/ ./config/
COPY database/ ./database/
COPY models/ ./models/
COPY scraper/ ./scraper/
COPY scripts/ ./scripts/
COPY utils/ ./utils/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create logs directory
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Default command
CMD ["python", "scripts/scrape_all.py"]

