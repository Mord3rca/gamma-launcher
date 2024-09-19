import re
import os.path

from bs4 import BeautifulSoup
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

    def _check_with_update(self, file: Path, info: dict, dl_dir: Path, hash: str) -> None:
        try:
            self.download(dl_dir, use_cached=True, hash=hash)
        except ConnectionError as e:
            raise HashError(f'Failed to redownload {file.name}\n  -> {e}')
        except HashError:
            raise HashError(f'{file.name} failed MD5 check after being redownloaded')

    def _check_without_update(self, file: Path, info: dict, dl_dir: Path, hash: str) -> None:
        if not file.exists():
            raise HashError(f'{file.name} not found on disk')

        if check_hash(file, hash):
            return

        raise HashError(f'{file.name} MD5 missmatch')

    def check(self, dl_dir: Path, update_cache: bool = False) -> None:
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

        if info.get('Download', '') not in self._url:
            raise HashError(f'Skipping {file.name} since ModDB info do not match download url')

        (self._check_with_update if update_cache else self._check_without_update)(file, info, dl_dir, hash)

    def download(self, to: Path, use_cached: bool = False, *args, **kwargs) -> Path:
        metadata = parse_moddb_data(self._iurl) if self._iurl else {}
        hash = metadata.get('MD5 Hash', None) if metadata.get('Download', '') in self._url else None
        id = id = self._url.split('/')[-1]
        s = re.search(f'/downloads/mirror/{id}/[^"]*', g_session.get(self._url).text)
        if not s:
            raise ModDBDownloadError(f"Download link not found when requesting {self._url}")

        self._url = g_session.get(f"https://www.moddb.com{s[0]}", allow_redirects=False).headers["location"]
        self._archive = to / os.path.basename(urlparse(self._url).path)
        return super().download(to, use_cached, hash=hash)
