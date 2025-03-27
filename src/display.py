from typing import Optional
from importlib import import_module
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

from constants import Coordinates
from exceptions import EPDModuleError

def create_composite_image(
    current_book: Optional[Path],
    past_books: list[Path],
    display_size: Coordinates,
    max_cols: int = 4,
    padding: int = 10,
):
    """Generate a dynamic layout for book covers on different resolutions."""

    # Create blank canvas with white background
    canvas = Image.new("1", display_size, 255)
    if not current_book:
        current_book = past_books[0]
        past_books = past_books[1:]
    # Calculate size for the currently reading book (scaled)
    current_img = Image.open(current_book)
    current_aspect = current_img.width / current_img.height
    current_height = int(display_size[1] * 0.75)  # 50% of display height
    current_width = int(current_height * current_aspect)
    current_img = current_img.resize((current_width, current_height))

    # Place currently reading book on the left
    canvas.paste(current_img, (padding, (display_size.y - current_height) // 2))

    # Calculate available space for past books
    grid_x_start = current_width + 2 * padding  # Start past books after current book
    grid_height = display_size.y - 2 * padding  # Height for past books

    # Dynamically determine the best grid size
    num_books = len(past_books)
    cols = min(max_cols, num_books)  # Use max_cols or fewer if not enough books
    rows = (num_books + cols - 1) // cols  # Calculate required rows

    # Set a uniform height for past books
    book_target_height = (grid_height - (rows - 1) * padding) // rows

    # Determine book size dynamically
    row_books = []
    row_height = 0
    # Place past books in a grid
    x_offset, y_offset = grid_x_start, padding
    for index, book in enumerate(past_books):
        img = Image.open(book)
        aspect = img.width / img.height
        book_width = int(book_target_height * aspect)
        img = img.resize((book_width, book_target_height))

        # Track max row height for even spacing
        row_books.append((img, x_offset, y_offset, book_width, book_target_height))
        row_height = max(row_height, book_target_height)

        # Move to next position
        x_offset += book_width + padding

        # If end of row, reset x_offset and move down
        if (index + 1) % cols == 0 or index == num_books - 1:
            # Paste all books in row (ensures even row spacing)
            for img, x, y, w, h in row_books:
                canvas.paste(
                    img, (x, y + (row_height - h) // 2)
                )  # Center vertically in row

            # Reset row tracking
            row_books = []
            x_offset = grid_x_start
            y_offset += row_height + padding
            row_height = 0

    return canvas


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
        raise EPDModuleError(f"Error: {epd_type} module not able to be initialised correctly. Check EPD_TYPE is set correctly for your device.")
    try:
        epd.init()
        epd.Clear()
        epd.display(epd.buffer(image))
    except Exception as e:
        EPDModuleError(f"Failed to use waveshare_epd to display image: {e}")


def _simulate_display(image: Image.Image) -> None:
    """Simulate the e-ink display on PC using Matplotlib."""
    plt.imshow(image)
    plt.axis("off")
    plt.show()
