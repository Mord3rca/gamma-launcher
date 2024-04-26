from .base import Base, g_session
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import re
import os.path
from typing import Dict


def parse_moddb_data(url: str) -> Dict[str, str]:
    soup = BeautifulSoup(g_session.get(url).text, features="html.parser")
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


class ModDBDownloadError(Exception):
    pass


class ModDB(Base):

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._orig_url = url
        self._filename = None

    @property
    def url(self) -> str:
        return self._orig_url

    @property
    def filename(self) -> str:
        if not self._filename:
            self._get_filename()

        return self._filename

    def _get_filename(self) -> None:
        id = self._url.split('/')[-1]
        s = re.search(f'/downloads/mirror/{id}/[^"]*', g_session.get(self._url).text)
        if not s:
            raise ModDBDownloadError(f"Download link not found when requesting {self._url}")
        location = g_session.get(f"https://www.moddb.com{s[0]}", allow_redirects=False).headers["location"]
        self._url = location
        self._filename = os.path.basename(urlparse(location).path)
