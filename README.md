# Book Dashboard

## Overview
Python-based project that displays a dashboard of book cover images on an e-ink display. It integrates with Goodreads to show recently read books, with the currently reading book emphasized. The project is designed to be deployed on a Raspberry Pi.

## Features
- Fetches book data (title, author, date read) from Goodreads.
- Integrated with Calibre to pick up covers locally. Falls back to downloading covers from Goodreads.
- Displays book covers dynamically on an e-ink display.
- Supports custom layouts.
- Runs on a Raspberry Pi with Waveshare e-Paper displays.

![dash preview](./img/dash.jpg)

## Raspberry Pi Setup
Ensure SPI is enabled on the Pi:
```sh
sudo raspi-config  # Enable SPI under 'Interfacing Options'
```

## Installation
### **1. Clone the Repository**
```sh
git clone https://github.com/yourusername/book_dashboard.git
cd book_dashboard
```

### **2. Set Up Python Environment**
#### Using `uv` (Recommended)
```sh
uv venv .venv
uv pip install -r requirements.txt
```
#### Using `venv` and `pip`
```sh
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
```

### **3. Set Up Environment Variables**
Create a `.env` file in the project root. The `.env.sample` in the repo gives all possible environment variables.
```bash
GOODREADS_USER_ID=your_user_id
CALIBRE_DB_PATH=/path/to/calibre/library # OPTIONAL
CALIBRE_LIBRARY_PATH=//hardymews/8hm/calibre/
EINK_DISPLAY_WIDTH=800
EINK_DISPLAY_HEIGHT=480
NUM_COLS=5 # number of columns in grid display
NUM_ROWS=3 # number of rows in grid display
EPD_TYPE=epd7in5 # see https://github.com/waveshare/e-Paper for yours. Use "TEST" for local testing with matplotlib.
```

### **4. Run the Dashboard**
```sh
uv run src/main.py
```
Or using Python:
```sh
python src/main.py
```

## Deployment with Docker
Note that this currently takes a long time to build due to needing a lot of system dependencies to correctly run `spidev` as well as cloning and compiling the waveshare dependencies. Will try to get this build time down at some point.
### **1. Build the Docker Image**
```sh
docker build -t book-dashboard .
```

On the Raspberry Pi Zero the network timeout can cause issues with TLS handshakes. If you run into this consider changing to a faster DNS, i.e.
```sh
sudo nano /etc/resolve.conf
```
and add in `nameserver 8.8.8.8` to the file before trying to rebuild.

### **2. Run the Container**
```sh
docker run --rm --env-file .env book-dashboard
```

To run the app on startup, add this to `crontab -e`:
```
@reboot /usr/bin/python3 /path/to/book_dashboard.py
```