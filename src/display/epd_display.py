from importlib import import_module

import matplotlib.pyplot as plt
from PIL import Image

from config.exceptions import EPDModuleError


def display_image(image: Image.Image, *, epd_type: str) -> None:
    if epd_type == "TEST":
        return _simulate_display(image)
    # Dynamically import the correct EPD module
    try:
        epd_module = import_module(f"waveshare_epd.{epd_type}")
        # Use the EPD class from the dynamically imported module
        epd = epd_module.EPD()
        print(f"Successfully imported {epd_type} driver.")
    except Exception:
        raise EPDModuleError(
            f"Error: {epd_type} module not able to be initialised correctly. Check EPD_TYPE is set correctly for your device."
        )
    try:
        epd.init()
        epd.Clear()
        Himage2 = Image.new("L", (epd.width, epd.height), 255)  # 255: clear the frame
        Himage2.paste(image, (10, 10))
        epd.display(epd.getbuffer(Himage2))
    except Exception as e:
        EPDModuleError(f"Failed to use waveshare_epd to display image: {e}")


def _simulate_display(image: Image.Image) -> None:
    """Simulate the e-ink display on PC using Matplotlib."""
    plt.imshow(image)
    plt.axis("off")
    plt.show()
