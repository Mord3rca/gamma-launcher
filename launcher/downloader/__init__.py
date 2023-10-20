from .github import Github
from .moddb import ModDB
from .base import Base

from urllib.parse import urlparse
from requests.exceptions import ConnectionError
from tenacity import retry, stop_after_attempt, wait_fixed
from pathlib import Path


def get_handler_for_url(url: str) -> Base:
    host = urlparse(url).hostname
    return {'github.com': Github, 'www.moddb.com': ModDB,}.get(
        host
    )(url)


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
)
def download_mod(url: str, download_dir: Path, use_cached: bool = True) -> Path:
    e = get_handler_for_url(url)
    file = Path(download_dir, e.filename)

    if file.is_file() and use_cached:
        print(f'  - Using cached {file.name}')
        return file

    print(f'  - Downloading {file.name}')
    try:
        e.download(file)
    except ConnectionError as e:
        print('  -> Failed, retrying...')
        file.unlink()
        raise e

    return file
