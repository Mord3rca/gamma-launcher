from .base import Base, g_session
from urllib.parse import urlparse

import re
import os.path


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
        location = g_session.get(f'https://www.moddb.com{s[0]}', allow_redirects=False).headers['location']
        self._url = location
        self._filename = os.path.basename(urlparse(location).path)
