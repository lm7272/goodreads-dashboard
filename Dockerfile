# Use a Raspberry Pi OS-compatible Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-dev python3-setuptools \
    libopenjp2-7 libtiff5-dev libjpeg-dev \
    git python3-spidev gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first and install dependencies
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Manually clone and install Waveshare e-Paper with a shallow clone
RUN git clone --depth=1 --branch master https://github.com/waveshare/e-Paper.git /tmp/e-Paper \
    && python -m pip install /tmp/e-Paper/RaspberryPi_JetsonNano/python \
    && rm -rf /tmp/e-Paper  # Cleanup to keep the image small

# Copy the rest of the application code
COPY . /app

# Set the entry point
CMD ["python", "src/main.py"]
