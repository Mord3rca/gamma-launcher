from .github import Github
from .moddb import ModDB
from .base import Base

from urllib.parse import urlparse
from tenacity import retry, TryAgain, stop_after_attempt
from pathlib import Path


def get_handler_for_url(url: str) -> Base:
    host = urlparse(url).hostname
    return {
        'github.com': Github,
        'www.moddb.com': ModDB,
    }.get(host)(url)


@retry(stop=stop_after_attempt(3))
def download_mod(url: str, download_dir: Path, use_cached: bool = True) -> Path:
    e = get_handler_for_url(url)
    file = Path(download_dir, e.filename)

    if file.is_file() and use_cached:
        print(f'  - Using cached {file.name}')
        return file

    print(f'  - Downloading {file.name}')
    try:
        e.download(file)
    except ConnectionError:
        print('  -> Failed, retrying...')
        file.unlink()
        raise TryAgain

    return file
