from pathlib import Path

import requests
from unidecode import unidecode

from config.constants import DEFAULT_HEADERS


def normalise_string(text: str) -> str:
    return unidecode(text).lower().replace("  ", " ")


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
