from hashlib import md5
from os.path import basename
from urllib.parse import urlparse

from requests import Session

g_session = Session()
g_session.headers.update({'User-Agent': 'pyGammaLauncher'})


class Base:

    def __init__(self, url: str) -> None:
        self._url = url
        self._md5 = None

    @property
    def url(self) -> str:
        return self._url

    @property
    def md5(self) -> str:
        if not self._md5:
            raise RuntimeError("md5 not calculated, please use download() first")

        return self._md5

    @property
    def filename(self) -> str:
        return basename(urlparse(self._url).path)

    def download(self, path: str) -> None:
        h = md5()
        with open(path, 'wb') as f:
            r = g_session.get(self._url)
            for chunk in r.iter_content(chunk_size=1 * 1024 * 1024):
                if chunk:
                    f.write(chunk)
                    h.update(chunk)
        self._md5 = h.hexdigest()
