FROM python:3.12-slim

# Cleaner logs, no .pyc files, no pip cache, default port
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5000

# Basic network tools (add nmap here only if your code actually calls it)
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping iproute2 net-tools \
    && rm -rf /var/lib/apt/lists/*

# Run as a normal user instead of root
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Install dependencies first so Docker caches this layer
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app and make the data folder writable
COPY --chown=appuser:appuser . .
RUN mkdir -p /app/data && chown appuser:appuser /app/data

USER appuser

EXPOSE 5000

# Docker marks the container unhealthy if the app stops responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/' % os.environ.get('PORT', '5000'))" || exit 1

# One worker keeps the live trend history consistent; threads handle concurrency
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120 --access-logfile - app.routes:app"]