import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Union

import requests

from constants import (
    DEFAULT_HEADERS,
    SHELF_TO_TIME_ATTRIBUTE_MAP,
    LOCAL_IMAGE_DIR,
    BookMetadata,
    GoodreadsBookMetadata,
    GoodreadsShelf,
)
from display import create_composite_image, display_covers
from environment import (
    get_calibre_db_path,
    get_calibre_library_path,
    get_display_size,
    get_epd_type,
    get_goodreads_user_id,
    get_number_of_read_books,
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
            user_read_at=map_goodreads_date_to_timestamp(
                item.find("user_read_at").text
            ),
            user_added_at=map_goodreads_date_to_timestamp(
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
    tagged_author_title = []
    for title, author, book_path in books:
        if (author, title) in tagged_author_title:
            continue
        tagged_author_title.append((author, title))
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
    """
    Takes a collection of goodreads books and plugs the gaps with local cover URL data.
    If no such cover exists in the calibre db then it will download the covers to some local
    directory.

    Args:
        goodreads_books (list[GoodreadsBookMetadata]): list of books pulled from the goodreads api
        calibre_books (list[BookMetadata]): list of calibre books that contains metadata on where the covers live

    Returns:
        list[BookMetadata]: enhanced list of books with all images now populated.
    """
    full_books: list[BookMetadata] = []
    for gr_book in goodreads_books:
        matching_calibre_books = [
            book
            for book in calibre_books
            if (gr_book.title == book.title) and (gr_book.author == book.author)
        ]
        if len(matching_calibre_books) == 1:
            matching_calibre_book = matching_calibre_books[0]
            gr_book = gr_book._replace(
                book_cover_path=matching_calibre_book.book_cover_path
            )
        elif not matching_calibre_books and gr_book.book_cover_url is not None:
            # download image locally
            img_data = requests.get(
                gr_book.book_cover_url,
                headers=DEFAULT_HEADERS,
            )
            if img_data.status_code == 200:
                LOCAL_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
                local_path = LOCAL_IMAGE_DIR / gr_book.book_cover_url.split(r'/')[-1]
                with open(local_path, "wb") as writer:
                    writer.write(img_data.content)

                gr_book = gr_book._replace(book_cover_path=Path(local_path))
        full_books.append(gr_book)

    return full_books


def get_cover_path(path: Union[str, Path]) -> Path:
    """Return the cover image path for a given book from local file."""
    if Path(path).exists():
        return Path(path)
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


def get_sorted_books_with_covers(
    user_id: int, limit: int, shelf: GoodreadsShelf
) -> list[GoodreadsBookMetadata]:
    goodreads_books = get_most_recent_goodreads_books(user_id, limit, shelf)
    calibre_books = fetch_calibre_books_from_goodreads_metadata(goodreads_books)

    return complete_book_metadata(goodreads_books, calibre_books)

def get_current_book_cover_path(goodreads_user_id: int) -> Optional[Path]:
    goodreads_currently_reading_books = get_sorted_books_with_covers(
        user_id=goodreads_user_id, limit=1, shelf=GoodreadsShelf.CURRENTLY_READING
    )
    if not goodreads_currently_reading_books:
        return None
    return get_cover_path(
        goodreads_currently_reading_books[0].book_cover_path
    )

def get_recently_read_book_cover_paths(goodreads_user_id: int, number_of_read_books: int) -> list[Path]:
    goodreads_read_books = get_sorted_books_with_covers(user_id=goodreads_user_id, limit=number_of_read_books, shelf=GoodreadsShelf.READ)
    return [
        get_cover_path(book.book_cover_path)
        for book in sorted(
            goodreads_read_books, key=lambda x: x.user_read_at, reverse=True
        )
        if get_cover_path(book.book_cover_path)
    ]

def main() -> None:
    goodreads_user_id = get_goodreads_user_id()
    number_of_read_books = get_number_of_read_books()

    current_book_path = get_current_book_cover_path(goodreads_user_id=goodreads_user_id)
    past_book_paths = get_recently_read_book_cover_paths(goodreads_user_id=goodreads_user_id, number_of_read_books=number_of_read_books)

    if not past_book_paths:
        print("Missing book covers!")
        exit()
    final_image = create_composite_image(
        current_book_path, past_book_paths, get_display_size()
    )

    display_covers(final_image, epd_type=get_epd_type())  # Display the image


if __name__ == "__main__":
    load_env_file()
    main()
