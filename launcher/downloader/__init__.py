from .github import Github
from .moddb import ModDB
from .base import Base

from urllib.parse import urlparse
from requests.exceptions import ConnectionError
from tenacity import retry, stop_after_attempt, wait_fixed
from pathlib import Path

from launcher.compat import file_digest


def get_handler_for_url(url: str) -> Base:
    host = urlparse(url).hostname
    return {
        'github.com': Github,
        'www.moddb.com': ModDB,
    }.get(host)(url)


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
)
def download_archive(
    url: str, download_dir: Path, use_cached: bool = True,
    hash_type: str = 'md5', hash: str = None
) -> Path:
    e = get_handler_for_url(url)
    file = Path(download_dir, e.filename)

    if file.is_file() and use_cached:
        if not hash:
            print(f'  - Using cached {file.name}')
            return file

        with open(file, 'rb') as f:
            fhash = file_digest(f, hash_type).hexdigest()

        if (fhash == hash):
            print(f'  - Using cached {file.name} ({hash})')
            return file

        print(f'  - Updating cache file {file.name}')
        file.unlink()  # Redownload

    print(f'  - Downloading {file.name}')
    try:
        e.download(file)
    except ConnectionError as e:
        print('  -> Failed, retrying...')
        file.unlink()
        raise e

    return file


def download_mod(*args, **kwargs) -> Path:
    return download_archive(*args, **kwargs)
