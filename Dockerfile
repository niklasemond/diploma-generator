FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zip \
    libreoffice \
    libreoffice-writer \
    default-jre \
    python3-uno \
    unoconv \
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

# Create a startup script
RUN echo '#!/bin/bash\n\
# Start LibreOffice headless mode\n\
/usr/lib/libreoffice/program/soffice --headless --accept="socket,host=127.0.0.1,port=8100;urp;" --nofirststartwizard & \n\
# Wait for LibreOffice to start\n\
sleep 5\n\
# Start the application\n\
exec gunicorn --bind 0.0.0.0:8080 app:app' > /app/start.sh && \
chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Run the application with the startup script
CMD ["/app/start.sh"] 