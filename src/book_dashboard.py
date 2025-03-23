import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union

import requests

from constants import (
    DEFAULT_HEADERS,
    SHELF_TO_TIME_ATTRIBUTE_MAP,
    BookMetadata,
    DisplayMode,
    GoodreadsBookMetadata,
    GoodreadsShelf,
)
from display import ENVIRONMENT_TO_DISPLAY_FUNCTION, create_composite_image
from environment import (
    get_calibre_db_path,
    get_calibre_library_path,
    get_display_size,
    get_goodreads_user_id,
    load_env_file,
)
from utils import map_goodreads_date_to_timestamp, normalise_string


def get_user_shelf_goodreads_books_metadata(
    user_id: int, shelf: GoodreadsShelf
) -> list[GoodreadsBookMetadata]:
    response = requests.get(
        f"https://www.goodreads.com/review/list_rss/{user_id}?shelf={shelf.value}",
        headers=DEFAULT_HEADERS,
    )
    if response.status_code != 200:
        return []
    root = ET.fromstring(response.content)

    return [
        GoodreadsBookMetadata(
            title=normalise_string(item.find("title").text),
            author=normalise_string(item.find("author_name").text),
            user_read_at=map_goodreads_date_to_timestamp(item.find("user_read_at").text),
            user_added_at=map_goodreads_date_to_timestamp(
                item.find("user_added_at").text if item.find("user_added_at") is not None else None
            ),
            book_cover_path=Path("/does/not/exist/"),
            book_cover_url=item.find("book_large_image_url").text,
        )
        for item in root.findall(".//item")
        if item is not None
    ]


def fetch_calibre_books_from_goodreads_metadata(
    goodreads_books: list[GoodreadsBookMetadata],
) -> list[BookMetadata]:
    DB_PATH = get_calibre_db_path()
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT title, author_sort, path FROM books WHERE title in {tuple([*[book.title for book in goodreads_books], ''])}"
    )

    books: list[tuple[int, str, str, str]] = cursor.fetchall()
    conn.close()
    calibre_books: list[BookMetadata] = []
    tagged_book_author = []
    for title, author, book_path in books:
        if (author, title) in tagged_book_author:
            continue
        tagged_book_author.append((author, title))
        calibre_books.append(
            BookMetadata(
                title=normalise_string(title),
                author=normalise_string(" ".join(author.split(", ")[::-1])),
                book_cover_path=Path(book_path),
            )
        )
    return calibre_books


def complete_book_metadata(
    goodreads_books: list[GoodreadsBookMetadata], calibre_books: list[BookMetadata]
) -> list[BookMetadata]:
    full_books: list[BookMetadata] = []
    for gr_book in goodreads_books:
        matching_calibre_books = [
            book
            for book in calibre_books
            if (gr_book.title == book.title) and (gr_book.author == book.author)
        ]
        if len(matching_calibre_books) == 1:
            matching_calibre_book = matching_calibre_books[0]
            gr_book = gr_book._replace(book_cover_path=matching_calibre_book.book_cover_path)
        elif not matching_calibre_books and gr_book.book_cover_url is not None:
            # download image locally
            img_data = requests.get(
                gr_book.book_cover_url,
                headers=DEFAULT_HEADERS,
            )
            if img_data.status_code == 200:
                local_path = f"images/{gr_book.book_cover_url.split(r'/')[-1]}"
                with open(local_path, "wb") as writer:
                    writer.write(img_data.content)

                gr_book = gr_book._replace(book_cover_path=Path(local_path))
        full_books.append(gr_book)

    return full_books


def get_cover_path(path: Union[str, Path]):
    """Return the cover image path for a given book from local file."""
    if Path(path).exists():
        return path
    cover_path = get_calibre_library_path() / path / "cover.jpg"
    return cover_path if cover_path.exists() else None


def get_most_recent_goodreads_books(
    user_id: int, limit: int, shelf: GoodreadsShelf
) -> list[GoodreadsBookMetadata]:
    goodreads_read_books = get_user_shelf_goodreads_books_metadata(user_id, shelf)
    return sorted(
        goodreads_read_books,
        key=lambda x: getattr(x, SHELF_TO_TIME_ATTRIBUTE_MAP[shelf]),
    )[-limit:]


def get_books(user_id: int, limit: int, shelf: GoodreadsShelf) -> list[GoodreadsBookMetadata]:
    goodreads_books = get_most_recent_goodreads_books(user_id, limit, shelf)
    calibre_books = fetch_calibre_books_from_goodreads_metadata(goodreads_books)

    return complete_book_metadata(goodreads_books, calibre_books)


if __name__ == "__main__":
    load_env_file()
    GOODREADS_USER_ID = get_goodreads_user_id()
    goodreads_read_books = get_books(GOODREADS_USER_ID, 12, GoodreadsShelf.READ)
    goodreads_currently_reading_books = get_books(
        GOODREADS_USER_ID, 1, GoodreadsShelf.CURRENTLY_READING
    )

    current_book_path = get_cover_path(goodreads_currently_reading_books[0].book_cover_path)
    past_books = [
        get_cover_path(book.book_cover_path)
        for book in sorted(goodreads_read_books, key=lambda x: x.user_read_at, reverse=True)
        if get_cover_path(book.book_cover_path)
    ]
    if not current_book_path or len(past_books) == 0:
        print("Missing book covers!")
        exit()
    final_image = create_composite_image(current_book_path, past_books, get_display_size())
    ENVIRONMENT_TO_DISPLAY_FUNCTION[DisplayMode.TEST](final_image, "viridis")  # Display on PC
