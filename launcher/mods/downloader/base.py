from cloudscraper import create_scraper
from os.path import basename
from pathlib import Path
from re import compile
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

    regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)(/archive/([\\w]+).zip)?")

    @property
    def archive(self) -> Path:
        if not self._archive:
            raise RuntimeError("archive not available, run download() first")

        return self._archive

    @property
    def url(self) -> str:
        return self._url

    def check(self, dl_dir: Path, update_cache: bool = False) -> None:
        return (dl_dir / basename(urlparse(self._url).path)).exists()

    def download(self, to: Path, use_cached=False, hash: str = None) -> Path:
        self._archive = self._archive or (to / basename(urlparse(self._url).path))

        # Special case for github.com archive link
        if 'github.com' in self._url:
            _, project, *_ = self.regexp_url.match(self._url).groups()
            self._archive = to / f"{project}-{basename(urlparse(self._url).path)}"

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

    def extract(self, to: Path, tmpdir: str = None) -> None:
        print(f'Extracting {self.archive}')
        extract_archive(self.archive, to)
