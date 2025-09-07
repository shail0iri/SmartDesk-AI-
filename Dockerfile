FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (needed for pandas/matplotlib)
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

# Use Render's PORT environment variable (free tier uses 10000)
ENV PORT=10000
EXPOSE $PORT

# Run with Gunicorn using the PORT environment variable
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
