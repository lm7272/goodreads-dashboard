from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import NamedTuple, Optional

## CONSTANTS
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
}


## ENUMS
class GoodreadsShelf(Enum):
    READ = "read"
    CURRENTLY_READING = "currently-reading"
    WANT_TO_READ = "want-to-read"


## DATA
class Coordinates(NamedTuple):
    x: int
    y: int


class BookMetadata(NamedTuple):
    title: str
    author: str
    book_cover_path: Path
    book_cover_url: Optional[str] = None
    user_read_at: Optional[datetime] = None
    user_added_at: Optional[datetime] = None


class GoodreadsBookMetadata(BookMetadata):
    user_read_at: datetime
    user_added_at: datetime


## MAPS
SHELF_TO_TIME_ATTRIBUTE_MAP = {
    GoodreadsShelf.READ: "user_read_at",
    GoodreadsShelf.CURRENTLY_READING: "user_added_at",
}
