from .base import Base
from .github import Github
from .moddb import ModDB

from urllib.parse import urlparse
from requests.exceptions import ConnectionError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from pathlib import Path

from launcher.hash import check_hash


class HashError(Exception):
    pass


def get_handler_for_url(url: str, host: str = None) -> Base:
    host = host or urlparse(url).hostname
    return {
        'base': Base,
        'github.com': Github,
        'www.moddb.com': ModDB,
    }.get(host)(url)


@retry(
    reraise=True,
    retry=retry_if_exception_type(ConnectionError),
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
)
def download_archive(
    url: str, download_dir: Path, use_cached: bool = True,
    hash_type: str = 'md5', hash: str = None,
    host: str = None
) -> Path:
    e = get_handler_for_url(url, host)
    file = Path(download_dir, e.filename)

    if file.is_file() and use_cached:
        if not hash:
            print(f'  - Using cached {file.name}')
            return file

        if check_hash(file, hash):
            print(f'  - Using cached {file.name} ({hash})')
            return file

        print(f'  - Updating cache file {file.name}')
        file.unlink()  # Redownload

    try:
        e.download(file)
    except ConnectionError as e:
        print('  -> Failed, retrying...')
        file.unlink()
        raise e

    # Just in case
    if hash and hash != e.md5():
        raise HashError("Checksum error for {file.name} from {url}")

    return file
