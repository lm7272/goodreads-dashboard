from book_dashboard.config.environment import (
    get_display_size,
    get_epd_type,
    get_goodreads_user_id,
    get_number_of_columns,
    get_number_of_rows,
    load_env_file,
)
from book_dashboard.config.exceptions import GoodreadsBookException
from book_dashboard.data.metadata_utils import (
    get_current_book_cover_path,
    get_recently_read_book_cover_paths,
)
from book_dashboard.display.display import create_composite_image, display_image


def main() -> None:
    goodreads_user_id = get_goodreads_user_id()
    num_cols = get_number_of_columns()
    num_rows = get_number_of_rows()
    number_of_read_books = num_cols * num_rows

    current_book_path = get_current_book_cover_path(goodreads_user_id=goodreads_user_id)
    past_book_paths = get_recently_read_book_cover_paths(
        goodreads_user_id=goodreads_user_id, number_of_read_books=number_of_read_books
    )

    if not past_book_paths:
        raise GoodreadsBookException("No read books found.")

    final_image = create_composite_image(
        current_book_path, past_book_paths, get_display_size(), max_cols=num_cols
    )

    display_image(final_image, epd_type=get_epd_type())  # Display the image


if __name__ == "__main__":
    load_env_file()
    main()
