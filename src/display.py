from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

from constants import Coordinates, DisplayMode


def create_composite_image(
    current_book: Path, past_books: list[Path], display_size: Coordinates
) -> Image.Image:
    """Generate the layout for the book covers."""
    canvas = Image.new("L", display_size, 255)  # White background

    # Load and place currently reading book
    current_img = Image.open(current_book).resize(Coordinates(250, 350))
    canvas.paste(current_img, Coordinates(20, 65))  # Positioned to the left

    # Load and place past books
    x_offset, y_offset = 300, 20  # Starting position
    book_size = Coordinates(100, 150)
    cols = 4  # Books per row

    for index, book in enumerate(past_books):
        img = Image.open(book).resize(book_size)
        canvas.paste(img, Coordinates(x_offset, y_offset))

        x_offset += book_size.x + 10  # Move right
        if (index + 1) % cols == 0:  # New row
            x_offset = 300
            y_offset += book_size.y + 10
    return canvas


def simulate_display(image: Image.Image, cmap: str) -> None:
    """Simulate the e-ink display on PC using Matplotlib."""
    plt.imshow(image, cmap=cmap)
    plt.axis("off")
    plt.show()


ENVIRONMENT_TO_DISPLAY_FUNCTION: dict[
    DisplayMode, Callable[[Image.Image, str], None]
] = {DisplayMode.TEST: simulate_display}
