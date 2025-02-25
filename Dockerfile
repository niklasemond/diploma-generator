FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zip \
    libreoffice \
    libreoffice-script-provider-python \
    python3-uno \
    unoconv \
    && rm -rf /var/lib/apt/lists/*

# Start LibreOffice in headless mode as a daemon
RUN mkdir -p /var/run/soffice && \
    nohup /usr/bin/soffice --headless --accept="socket,host=127.0.0.1,port=8100;urp;" --nofirststartwizard > /dev/null 2>&1 &

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads output

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Create a startup script
RUN echo '#!/bin/bash\n\
soffice --headless --accept="socket,host=127.0.0.1,port=8100;urp;" --nofirststartwizard & \
sleep 5 && \
exec gunicorn --bind 0.0.0.0:8080 app:app' > /app/start.sh && \
chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Run the application with the startup script
CMD ["/app/start.sh"] 