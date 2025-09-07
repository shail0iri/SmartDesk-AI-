FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (needed for pandas/matplotlib)
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

EXPOSE 8000

# Run with Gunicorn (production server for Flask)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
