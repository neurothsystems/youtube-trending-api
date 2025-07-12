FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

COPY minimal_requirements.txt .
RUN pip install --no-cache-dir -r minimal_requirements.txt

COPY simple_server.py .
COPY config.ini .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "simple_server.py"]