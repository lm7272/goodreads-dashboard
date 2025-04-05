from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import Element

import requests
from unidecode import unidecode

from config.constants import DEFAULT_HEADERS
from config.exceptions import GoodreadsBookException


def normalise_string(text: str) -> str:
    return unidecode(text).lower().replace("  ", " ")


def get_item_text(item: Element, text_to_find: str) -> Optional[str]:
    elt = item.find(text_to_find)
    return elt.text if elt is not None else None


def get_item_text_with_raise(item: Element, text_to_find: str) -> str:
    txt = get_item_text(item, text_to_find)
    if txt is None:
        raise GoodreadsBookException(
            f"Couldn't find {text_to_find} inside of item {item.text}"
        )
    return txt


def download_image_from_url(url: str, target_path: Path) -> bool:
    img_data = requests.get(
        url,
        headers=DEFAULT_HEADERS,
    )
    if img_data.status_code == 200:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as writer:
            writer.write(img_data.content)
        return True
    return False
