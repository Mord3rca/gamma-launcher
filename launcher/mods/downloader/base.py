""
from cloudscraper import create_scraper
from os.path import basename
from pathlib import Path
from re import compile
from requests.exceptions import ConnectionError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from tqdm import tqdm
from urllib.parse import urlparse

from launcher import __version__
from launcher.exceptions import HashError
from launcher.hash import check_hash
from launcher.archive import extract_archive

g_session = create_scraper(
    browser={
       "custom": f"pyGammaLauncher/{__version__}"
    }
)
"`cloudscraper` scraper object used for all HTTP requests"


class DefaultDownloader:
    """Default downloader used to get an URL and save it to a file

    Argument(s):
    * url -- Remote file URL to download

    Keywords argument(s):
    * filename -- Force a filename instead of using URL basename
    * filehash -- File checksum if known
    """

    regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)(/archive/([\\w]+).zip)?")

    def __init__(self, url: str, filename: str = None, filehash: str = None) -> None:
        self._url = url
        self._archive = None
        self._archivehash = filehash

        self._user_wanted_name = filename

    def _set_archive_name(self, to: Path) -> None:
        if self._archive:
            return

        if self._user_wanted_name:
            self._archive = to / self._user_wanted_name
            return

        if 'github.com' in self._url:
            _, project, *_ = self.regexp_url.match(self._url).groups()
            self._archive = to / f"{project}-{basename(urlparse(self._url).path)}"
            return

        self._archive = to / basename(urlparse(self._url).path)

    @property
    def archive(self) -> Path:
        "Return a `pathlib.Path` object of the downloaded archive"
        if not self._archive:
            raise RuntimeError("archive not available, run check() or download() first")

        return self._archive

    @property
    def url(self) -> str:
        "Get URL"
        return self._url

    def _check_if_non_exist(self, to: Path, update_cache: bool = False) -> None:
        if not update_cache:
            raise HashError(f'Hash verification failed since {self._archive.name} does not exist')

        self.download(to)

        if self._archivehash:
            if not check_hash(self._archive, self._archivehash):
                raise HashError(f'Hash verification failed after download for {self._archive.name}')

    def _check_if_exist(self, to: Path, update_cache: bool = False) -> None:
        if not self._archivehash:
            return

        if check_hash(self._archive, self._archivehash):
            return

        if update_cache:
            self._archive.unlink()
            self._check_if_non_exist(to, update_cache)
            return

        raise HashError(f'Hash verification failed for {self._archive.name}')

    def check(self, to: Path, update_cache: bool = False) -> None:
        "Method used in `launcher.commands.CheckMD5` to verify file presence & checksum"
        self._set_archive_name(to)

        (self._check_if_exist if self._archive.exists() else self._check_if_non_exist)(to, update_cache)

    @retry(
        before_sleep=lambda _: print("Connection error, retrying in 30s..."),
        reraise=True,
        retry=retry_if_exception_type(ConnectionError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(30)
    )
    def download(self, to: Path, use_cached=False, hash: str = None) -> Path:
        """Download the file

        Argument(s):
        * to -- Folder to save the file

        Keyword argument(s):
        * use_cached -- If set to True, no requests will be done if the file exists
        * hash -- If set in constructor or here, file checksum will be checked

        Return a `pathlib.Path` object like `self.archive`
        """
        self._set_archive_name(to)

        hash = hash or self._archivehash

        if self._archive.exists() and use_cached:
            if not hash:
                return self._archive

            if check_hash(self._archive, hash):
                return self._archive

        r = g_session.get(self._url, stream=True)
        r.raise_for_status()
        with open(self._archive, "wb") as f, tqdm(
            desc=f"  - Downloading {self._archive.name} ({self._url})",
            unit="iB", unit_scale=True, unit_divisor=1024
        ) as progress:
            for chunk in r.iter_content(chunk_size=1 * 1024 * 1024):
                if chunk:
                    progress.update(f.write(chunk))

        return self._archive

    def extract(self, to: Path) -> None:
        """Extract the dowloaded archive

        Argument(s):
        * to -- Path object pointing to the directory to use for extraction
        """
        extract_archive(self.archive, to)
