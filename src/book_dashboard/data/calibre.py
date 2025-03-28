import sqlite3
from pathlib import Path

from utils.common import normalise_string

from book_dashboard.config.constants import BookMetadata, GoodreadsBookMetadata
from book_dashboard.config.environment import get_calibre_db_path


def get_calibre_books_from_db(
    book_titles: tuple[str],
) -> list[tuple[str, str, str, str]]:
    db_path = get_calibre_db_path()
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT title, author_sort, path FROM books WHERE title in {book_titles}"
    )

    books: list[tuple[int, str, str, str]] = cursor.fetchall()
    conn.close()
    return books


def fetch_calibre_books_from_goodreads_metadata(
    goodreads_books: list[GoodreadsBookMetadata],
) -> list[BookMetadata]:
    DB_PATH = get_calibre_db_path()
    if not DB_PATH.exists():
        return []
    books = get_calibre_books_from_db(
        book_titles=tuple([*[book.title for book in goodreads_books], ""])
    )
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
