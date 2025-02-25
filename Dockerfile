FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zip \
    libreoffice \
    libreoffice-writer \
    default-jre \
    python3-uno \
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
# Start LibreOffice headless mode with resource limits\n\
ulimit -n 1024\n\
for port in $(seq 8100 8102); do\n\
    /usr/lib/libreoffice/program/soffice \
    --headless \
    --accept="socket,host=127.0.0.1,port=$port;urp;" \
    --nofirststartwizard \
    --nologo \
    --nodefault \
    --norestore \
    & \n\
done\n\
\n\
# Wait for LibreOffice instances to start\n\
sleep 5\n\
\n\
# Start the application with limited workers\n\
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

# Run the application with the startup script
CMD ["/app/start.sh"] 