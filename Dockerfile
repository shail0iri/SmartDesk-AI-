FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas3-base \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Use port 10000 for Render
EXPOSE 10000

# ✅ FIXED: Use hardcoded port 10000 instead of $PORT variable
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
