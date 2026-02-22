from cloudscraper import create_scraper
from os.path import basename
from pathlib import Path
from re import compile
from requests.exceptions import ConnectionError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from tqdm import tqdm
from typing import cast
from urllib.parse import urlparse

from launcher import __version__
from launcher.hash import check_hash
from launcher.archive import extract_archive

g_session = create_scraper(
    browser={
       "custom": f"pyGammaLauncher/{__version__}"
    }
)


class DefaultDownloader:

    regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)(/archive/([\\w]+).zip)?")

    def __init__(self, url: str, filename: str = "", filehash: str = "") -> None:
        self._url = url
        self._archive = cast(Path, None)  # Will be set when download() is called
        self._archivehash = filehash

        self._user_wanted_name = filename

    def _set_archive_name(self, to) -> None:
        if self._archive:
            return

        if self._user_wanted_name:
            self._archive = to / self._user_wanted_name
            return

        if 'github.com' in self._url:
            _, project, *_ = self.regexp_url.match(self._url).groups()  # type: ignore[union-attr]
            self._archive = to / f"{project}-{basename(urlparse(self._url).path)}"
            return

        self._archive = to / basename(urlparse(self._url).path)

    @property
    def archive(self) -> Path:
        if not self._archive:
            raise RuntimeError("archive not available, run download() first")

        return self._archive

    @property
    def url(self) -> str:
        return self._url

    def check(self, dl_dir: Path, update_cache: bool = False) -> bool:
        return (dl_dir / basename(urlparse(self._url).path)).exists()

    @retry(
        before_sleep=lambda _: print("Connection error, retrying in 30s..."),
        reraise=True,
        retry=retry_if_exception_type(ConnectionError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(30)
    )
    def download(self, to: Path, use_cached=False, hash: str = "") -> Path:
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
        extract_archive(str(self.archive), str(to))
