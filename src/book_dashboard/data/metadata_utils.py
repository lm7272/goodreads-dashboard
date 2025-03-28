from pathlib import Path
from typing import Optional, Union


from book_dashboard.config.constants import (
    BookMetadata,
    GoodreadsBookMetadata,
    GoodreadsShelf,
)
from book_dashboard.config.environment import (
    get_calibre_library_path,
    get_local_image_dir,
)
from book_dashboard.data.calibre import (
    fetch_calibre_books_from_goodreads_metadata,
)
from book_dashboard.data.goodreads import (
    get_most_recent_goodreads_books,
)
from book_dashboard.utils.common import (
    download_image_from_url,
)


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
            local_path = get_local_image_dir() / gr_book.book_cover_url.split(r"/")[-1]
            if not local_path.exists():
                download_image_from_url(gr_book.book_cover_url, local_path)
            gr_book = gr_book._replace(book_cover_path=local_path)
        full_books.append(gr_book)

    return full_books


def get_cover_path(path: Union[str, Path]) -> Path:
    """Return the cover image path for a given book from local file."""
    if Path(path).exists():
        return Path(path)
    caliber_cover_path = get_calibre_library_path() / path / "cover.jpg"
    return caliber_cover_path if caliber_cover_path.exists() else None


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
    return get_cover_path(goodreads_currently_reading_books[0].book_cover_path)


def get_recently_read_book_cover_paths(
    goodreads_user_id: int, number_of_read_books: int
) -> list[Path]:
    goodreads_read_books = get_sorted_books_with_covers(
        user_id=goodreads_user_id, limit=number_of_read_books, shelf=GoodreadsShelf.READ
    )
    return [
        get_cover_path(book.book_cover_path)
        for book in sorted(
            goodreads_read_books, key=lambda x: x.user_read_at, reverse=True
        )
        if get_cover_path(book.book_cover_path)
    ]
