from datetime import datetime
from typing import Optional

from unidecode import unidecode


def map_goodreads_date_to_timestamp(ts: Optional[str]) -> datetime:
    if ts is None:
        return datetime(1970, 1, 1)
    return datetime.strptime(ts, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)


def normalise_string(text: str) -> str:
    return unidecode(text).lower().replace("  ", " ")
