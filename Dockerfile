# Use a lightweight Python base image
FROM python:3.11-slim

# Install git (needed for Waveshare)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libspi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements.txt first (for better caching)
COPY requirements.txt /app/

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . /app/

# Run the app
CMD ["python", "src/main.py"]
