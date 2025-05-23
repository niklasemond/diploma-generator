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

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Create necessary directories and set permissions
RUN mkdir -p uploads output && \
    chown -R appuser:appuser /app

# Configure Redis
RUN sed -i 's/bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf && \
    sed -i 's/protected-mode yes/protected-mode no/g' /etc/redis/redis.conf && \
    sed -i 's/databases 16/databases 32/g' /etc/redis/redis.conf && \
    echo "maxmemory 128mb" >> /etc/redis/redis.conf && \
    echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /var/lib/redis && \
    chown -R appuser:appuser /var/log/redis && \
    chown -R appuser:appuser /etc/redis

# Switch to non-root user
USER appuser

# Create and activate virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements first to leverage Docker cache
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PATH="/usr/lib/libreoffice/program:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONMALLOC=malloc
ENV PYTHONMALLOCSTATS=1

# Create a startup script that manages LibreOffice instances
RUN echo '#!/bin/bash\n\
# Start Redis server directly\n\
redis-server /etc/redis/redis.conf &\n\
\n\
# Wait for Redis to start\n\
until redis-cli ping; do\n\
    echo "Waiting for Redis..."\n\
    sleep 1\ndone\n\
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
celery -A tasks worker --loglevel=info --concurrency=1 --max-tasks-per-child=5 & \n\
\n\
# Start the application\n\
exec gunicorn \
    --bind 0.0.0.0:8080 \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --max-requests 50 \
    --max-requests-jitter 10 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    app:app' > /app/start.sh && \
chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Run the application with the startup script
CMD ["/app/start.sh"] 