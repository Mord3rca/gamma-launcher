import re
import os.path

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict

from launcher.hash import check_hash
from launcher.exceptions import HashError, ModDBDownloadError
from launcher.mods.downloader.base import DefaultDownloader, g_session


def parse_moddb_data(url: str) -> Dict[str, str]:
    r = g_session.get(url)

    if r.status_code != 200:
        r.raise_for_status()

    soup = BeautifulSoup(r.text, features="html.parser")
    result = {}

    for i in soup.body.find_all('div', attrs={'class': "row clear"}):
        try:
            name = i.h5.text
            value = i.span.text.strip()
        except AttributeError:
            # if div have no h5 or span child, just ignore it.
            continue

        # We can parse more, but we don't need it.
        if name in ('Filename', 'MD5 Hash'):
            result[name] = value
    try:
        result['Download'] = soup.find(id='downloadmirrorstoggle')['href'].strip()
    except TypeError:
        pass

    return result


class ModDBDownloader(DefaultDownloader):

    def _get_download_url(self, url: str) -> str:
        id = url.split('/')[-1]
        s = re.search(f'/downloads/mirror/{id}/[^"]*', g_session.get(url).text)
        if not s:
            raise ModDBDownloadError(f"Download link not found when requesting {url}")

        return g_session.get(f"https://www.moddb.com{s[0]}", allow_redirects=False).headers["location"]

    def check(self, dl_dir: Path, update_cache: bool = False) -> None:  # noqa: C901
        if not self._iurl:
            raise HashError(f'No info_url related to {self.name} mod')

        try:
            info = parse_moddb_data(self._iurl)
            file = dl_dir / info['Filename']
            hash = info['MD5 Hash']
        except ConnectionError as e:
            raise HashError(f'Error while fetching moddb page for {self._iurl}\n  -> {e}')
        except KeyError:
            raise HashError(f'Error while parsing moddb page for {self._iurl}')
        except HTTPError as e:
            raise HashError(f'ModDB parsing error for {self._iurl}\n -> {e}')

        if info.get('Download', '') not in self._url:
            raise HashError(f'Skipping {file.name} since ModDB info do not match download url')

        self._url = self._get_download_url(self._url)
        self._archive = file

        if not self._archive.exists():
            if update_cache:
                super().download(dl_dir)
            return

        if check_hash(self._archive, hash):
            return

        if not update_cache:
            raise HashError(f'{file.name} MD5 missmatch')

        self._archive.unlink()
        super().download(dl_dir)
        super().download(dl_dir, use_cached=True, hash=hash)  # to check hash

    def download(self, to: Path, use_cached: bool = False, *args, **kwargs) -> Path:
        try:
            metadata = parse_moddb_data(self._iurl) if self._iurl else {}
        except Exception:
            metadata = {}

        hash = metadata.get('MD5 Hash', None) if metadata.get('Download', '') in self._url else None

        self._url = self._get_download_url(self._url)
        self._archive = to / os.path.basename(urlparse(self._url).path)
        return super().download(to, use_cached, hash=hash)
