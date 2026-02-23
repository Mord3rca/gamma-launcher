import re

from bs4 import BeautifulSoup
from pathlib import Path
from requests.exceptions import HTTPError
from typing import Dict

from launcher.exceptions import HashError, ModDBDownloadError
from launcher.mods.downloader.base import DefaultDownloader, g_session


class ModDBDownloader(DefaultDownloader):

    def __init__(self, url: str, iurl: str) -> None:
        super().__init__(url)
        self._iurl = iurl

    @staticmethod
    def _parse_moddb_metadata(url: str) -> Dict[str, str]:
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

    @staticmethod
    def _get_download_url(url: str) -> str:
        id = url.split('/')[-1]
        s = re.search(f'/downloads/mirror/{id}/[^"]*', g_session.get(url).text)
        if not s:
            raise ModDBDownloadError(f"Download link not found when requesting {url}")

        return g_session.get(f"https://www.moddb.com{s[0]}", allow_redirects=False).headers["location"]

    def _set_vars_from_metadata(self):
        if not self._iurl:
            return

        try:
            metadata = self._parse_moddb_metadata(self._iurl) if self._iurl else {}

            self._archivehash = metadata.get('MD5 Hash', None)
            self._user_wanted_name = metadata.get('Filename', None)
        except HTTPError:
            metadata = {}

        return metadata

    def check(self, to: Path, update_cache: bool = False) -> None:
        if not self._iurl:
            raise HashError('No Info URL provided for this mod')

        metadata = self._set_vars_from_metadata()

        if not self._user_wanted_name:
            raise ModDBDownloadError(f'Could not find Filename in {self._iurl}')

        if not self._archivehash:
            raise ModDBDownloadError(f'Could not find archive hash in {self._iurl}')

        if metadata.get('Download', '') not in self._url:
            raise ModDBDownloadError(f'Skipping {self._user_wanted_name} since ModDB info do not match download url')

        self._url = self._get_download_url(self._url)

        super().check(to, update_cache)

    def download(self, to: Path, use_cached: bool = False, *args, **kwargs) -> Path:
        self._set_vars_from_metadata()
        self._url = self._get_download_url(self._url)

        return super().download(to, use_cached)
