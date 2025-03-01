FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zip \
    libreoffice \
    libreoffice-writer \
    default-jre \
    python3-uno \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p uploads output

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PATH="/usr/lib/libreoffice/program:${PATH}"
ENV PYTHONUNBUFFERED=1

# Create a startup script that manages LibreOffice instances
RUN echo '#!/bin/bash\n\
# Start Redis server with proper configuration\n\
redis-server /etc/redis/redis.conf --daemonize yes\n\
\n\
# Wait for Redis to start\n\
until redis-cli ping; do\n\
    sleep 1\n\
done\n\
\n\
# Start a single LibreOffice instance\n\
/usr/lib/libreoffice/program/soffice \
--headless \
--accept="socket,host=127.0.0.1,port=8100;urp;" \
--nofirststartwizard \
--nologo \
--nodefault \
--norestore \
& \n\
\n\
# Wait for services to start\n\
sleep 5\n\
\n\
# Start the Celery worker\n\
celery -A tasks worker --loglevel=info --concurrency=1 & \n\
\n\
# Start the application\n\
exec gunicorn \
    --bind 0.0.0.0:8080 \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --max-requests 50 \
    --max-requests-jitter 10 \
    app:app' > /app/start.sh && \
chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Update Redis configuration for multiple databases
RUN sed -i 's/bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf && \
    sed -i 's/protected-mode yes/protected-mode no/g' /etc/redis/redis.conf && \
    sed -i 's/databases 16/databases 32/g' /etc/redis/redis.conf && \
    echo "maxmemory 256mb" >> /etc/redis/redis.conf && \
    echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf

# Run the application with the startup script
CMD ["/app/start.sh"] 