from cloudscraper import create_scraper
from os.path import basename
from pathlib import Path
from re import compile
from typing import Optional
from requests.exceptions import ConnectionError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from tqdm import tqdm
from urllib.parse import urlparse

from launcher import __version__
from launcher.hash import check_hash
from launcher.mods.archive import extract_archive

g_session = create_scraper(
    browser={
       "custom": f"pyGammaLauncher/{__version__}"
    }
)


class DefaultDownloader:
    # Attributes expected to be provided by DefaultInstaller
    _url: str
    _iurl: Optional[str]
    _archive: Optional[Path]
    _revision: Optional[str]

    regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)(/archive/([\\w]+).zip)?")

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
    def download(self, to: Path, use_cached: bool = False, **kwargs) -> Path:
        hash = kwargs.get('hash', '')
        self._archive = self._archive or (to / basename(urlparse(self._url).path))

        # Special case for github.com archive link
        if 'github.com' in self._url:
            match = self.regexp_url.match(self._url)
            if match:
                _, project, *_ = match.groups()
                self._archive = to / f"{project}-{basename(urlparse(self._url).path)}"

        if self._archive.exists() and use_cached:
            if not hash:
                return self._archive

            if isinstance(hash, str) and check_hash(self._archive, hash):
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

    def extract(self, to: Path, **kwargs) -> None:
        tmpdir = kwargs.get('tmpdir')
        print(f'Extracting {self.archive}')
        extract_archive(str(self.archive), str(to))

    def revision(self) -> Optional[str]:
        return None
