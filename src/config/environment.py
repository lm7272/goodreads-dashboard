import os
from pathlib import Path

from config.constants import Coordinates


def load_env_file(filepath=Path(".env")):
    """Load environment variables from a .env file."""
    if filepath.exists():
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore comments and empty lines
                    key, value = line.split("=", 1)
                    os.environ[key] = value  # Set environment variable


def get_epd_type() -> str:
    return os.getenv("EPD_TYPE", "TEST")


def get_goodreads_user_id() -> int:
    return int(os.getenv("GOODREADS_USER_ID"))


def get_number_of_columns() -> int:
    return int(os.getenv("NUM_COLS", 3))


def get_number_of_rows() -> int:
    return int(os.getenv("NUM_ROWS", 4))


def get_calibre_library_path() -> Path:
    return Path(os.getenv("CALIBRE_LIBRARY_PATH", "/a/path/that/does/not/exist"))


def get_calibre_db_path() -> Path:
    return get_calibre_library_path() / "metadata.db"


def get_display_size() -> Coordinates:
    return Coordinates(
        int(os.getenv("EINK_DISPLAY_WIDTH", 800)),
        int(os.getenv("EINK_DISPLAY_HEIGHT", 480)),
    )


def get_local_image_dir() -> Path:
    return Path(os.getenv("LOCAL_IMAGE_DIR", "/tmp/cover_images"))
