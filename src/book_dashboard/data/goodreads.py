import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from book_dashboard.config.constants import (
    DEFAULT_HEADERS,
    SHELF_TO_TIME_ATTRIBUTE_MAP,
    GoodreadsBookMetadata,
    GoodreadsShelf,
)
from book_dashboard.config.exceptions import GoodreadsBookException
from book_dashboard.utils.common import normalise_string


def _map_goodreads_date_to_timestamp(ts: Optional[str]) -> datetime:
    if ts is None:
        return datetime(1970, 1, 1)
    return datetime.strptime(ts, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)


def get_goodreads_shelf_api_data(
    user_id: int, shelf: GoodreadsShelf
) -> Optional[ET.Element]:
    url = f"https://www.goodreads.com/review/list_rss/{user_id}?shelf={shelf.value}"
    response = requests.get(
        url,
        headers=DEFAULT_HEADERS,
    )
    if (status_code := response.status_code) != 200:
        raise GoodreadsBookException(
            f"Goodreads shelf {shelf} returned status code {status_code} from {url}"
        )
    return ET.fromstring(response.content)


def get_goodreads_metadata(
    user_id: int, shelf: GoodreadsShelf
) -> list[GoodreadsBookMetadata]:
    root = get_goodreads_shelf_api_data(user_id, shelf)

    return [
        GoodreadsBookMetadata(
            title=normalise_string(item.find("title").text),
            author=normalise_string(item.find("author_name").text),
            user_read_at=_map_goodreads_date_to_timestamp(
                item.find("user_read_at").text
            ),
            user_added_at=_map_goodreads_date_to_timestamp(
                item.find("user_added_at").text
                if item.find("user_added_at") is not None
                else None
            ),
            book_cover_path=Path("/does/not/exist/"),
            book_cover_url=item.find("book_large_image_url").text,
        )
        for item in root.findall(".//item")
        if item is not None
    ]


def get_most_recent_goodreads_books(
    user_id: int, limit: int, shelf: GoodreadsShelf
) -> list[GoodreadsBookMetadata]:
    goodreads_read_books = get_goodreads_metadata(user_id, shelf)
    return sorted(
        goodreads_read_books,
        key=lambda x: getattr(x, SHELF_TO_TIME_ATTRIBUTE_MAP[shelf]),
    )[-limit:]
