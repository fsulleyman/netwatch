FROM python:3.12-slim

# Network tools your app likely shells out to (remove what you don't use)
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping iproute2 nmap net-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app.routes:app"]