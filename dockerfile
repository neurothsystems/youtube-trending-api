# V6.0 YouTube Trending Analyzer Dockerfile
# Clean V6.0-only container without legacy code
FROM python:3.11-slim

# Metadata
LABEL version="6.0"
LABEL description="V6.0 YouTube Trending Analyzer - MOMENTUM Algorithm + Trending Pages"
LABEL maintainer="TopMetric.ai"

# Set working directory
WORKDIR /app

# Install system dependencies for V6.0 scraping
RUN apt-get update && apt-get install -y \
    # Basic build tools
    gcc \
    g++ \
    libc-dev \
    # XML/HTML parsing for BeautifulSoup
    libxml2-dev \
    libxslt-dev \
    # SSL for HTTPS requests
    ca-certificates \
    # Optional: Chrome for Selenium (if needed)
    chromium \
    chromium-driver \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash v6user
RUN chown -R v6user:v6user /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy V6.0 application code
COPY core/ ./core/
COPY services/ ./services/
COPY main_server.py .

# Copy configuration files
COPY config/ ./config/
RUN mkdir -p logs

# Create example config if not provided
RUN if [ ! -f config/v6_config.yaml ]; then \
        echo "Creating default V6.0 config..." && \
        python -c "from services.config_manager import ConfigManager; ConfigManager('config')"; \
    fi

# Set permissions
RUN chown -R v6user:v6user /app

# Switch to non-root user
USER v6user

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV V6_VERSION=6.0
ENV V6_ARCHITECTURE=clean
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:$PORT/health', timeout=5)" || exit 1

# Expose port
EXPOSE 8000

# V6.0 startup command
CMD ["python", "main_server.py"]

# ===============================================
# V6.0 DOCKER BUILD & RUN COMMANDS:
# ===============================================
# 
# Build V6.0 image:
# docker build -t youtube-trending-v6 .
# 
# Run V6.0 container:
# docker run -d \
#   --name youtube-trending-v6 \
#   -p 8000:8000 \
#   -e YOUTUBE_API_KEY=your_api_key_here \
#   -e V6_DEFAULT_REGION=DE \
#   -v $(pwd)/config:/app/config \
#   -v $(pwd)/logs:/app/logs \
#   youtube-trending-v6
# 
# Run with custom config:
# docker run -d \
#   --name youtube-trending-v6 \
#   -p 8000:8000 \
#   -e YOUTUBE_API_KEY=your_api_key_here \
#   -v $(pwd)/custom_config.yaml:/app/config/v6_config.yaml \
#   youtube-trending-v6
# 
# Development mode (with code mounting):
# docker run -it \
#   --name youtube-trending-v6-dev \
#   -p 8000:8000 \
#   -e YOUTUBE_API_KEY=your_api_key_here \
#   -v $(pwd):/app \
#   youtube-trending-v6 \
#   python main_server.py
# 
# Check logs:
# docker logs youtube-trending-v6
# 
# Execute commands inside container:
# docker exec -it youtube-trending-v6 bash
#
# Test API inside container:
# docker exec youtube-trending-v6 \
#   python -c "from core.api_client import YouTubeAPIClient; print(YouTubeAPIClient().test_connection())"
