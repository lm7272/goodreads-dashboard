import os
from pathlib import Path

from constants import Coordinates


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


# No auto-loading here
# Values are fetched dynamically at runtime
def get_goodreads_user_id() -> int:
    return os.getenv("GOODREADS_USER_ID")


def get_calibre_library_path() -> Path:
    return Path(os.getenv("CALIBRE_LIBRARY_PATH", "/a/path/that/does/not/exist"))


def get_calibre_db_path() -> Path:
    return get_calibre_library_path() / "metadata.db"


def get_display_size() -> Coordinates:
    return Coordinates(
        int(os.getenv("EINK_DISPLAY_WIDTH", 800)),
        int(os.getenv("EINK_DISPLAY_HEIGHT", 480)),
    )
