FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and required analysis tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the Celery worker
CMD ["celery", "-A", "app.tasks.worker.celery_app", "worker", "--loglevel=info"]
