# Aktualisiertes Dockerfile für modulares System
FROM python:3.9-slim

WORKDIR /app

# System-Dependencies (bleibt gleich)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies installieren
COPY minimal_requirements.txt .
RUN pip install --no-cache-dir -r minimal_requirements.txt

# ALLE Python-Dateien kopieren (wichtig!)
COPY trending_algorithm.py .
COPY modular_server.py .
COPY simple_server.py .
COPY config.ini .

# Port freigeben
EXPOSE 8000

# Environment-Variablen
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ⚠️ WICHTIG: Modularen Server starten statt simple_server.py
CMD ["python", "modular_server.py"]
