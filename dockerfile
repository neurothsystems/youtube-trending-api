# V6.0 YouTube Trending Analyzer - Render-optimiert
FROM python:3.11-slim

# Render-spezifische Labels
LABEL version="6.0-render"
LABEL description="V6.0 YouTube Trending Analyzer - Render-optimiert"

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies (minimal für Render)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc-dev \
    libxml2-dev \
    libxslt-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python Build-Tools aktualisieren
RUN pip install --upgrade pip setuptools wheel

# Requirements separat kopieren (für besseres Caching)
COPY requirements.txt .

# Dependencies installieren (mit Render-optimierten Flags)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# V6.0 Code kopieren
COPY core/ ./core/
COPY services/ ./services/
COPY main_server.py .

# Config-Ordner erstellen
RUN mkdir -p config logs

# Standard-Config erstellen falls nicht vorhanden
RUN echo "default_region: DE" > config/v6_config.yaml

# Port für Render
ENV PORT=8000
EXPOSE $PORT

# Render-spezifische Environment Variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Health-Check für Render
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get(f'http://localhost:{os.environ.get(\"PORT\", 8000)}/health', timeout=5)" || exit 1

# Render-optimierter Startup
CMD python main_server.py

# ===============================================
# RENDER DEPLOYMENT NOTES:
# ===============================================
# 
# Dieser Dockerfile ist speziell für Render optimiert:
# 1. Python 3.11 (stabile Version, nicht 3.13)
# 2. Minimale System-Dependencies
# 3. Optimierte pip-Installation
# 4. PORT Environment Variable für Render
# 5. Health-Check für Monitoring
# 6. PYTHONPATH für saubere Imports
# 
# Render Build Command: (automatisch durch Dockerfile)
# Render Start Command: (automatisch durch CMD)
