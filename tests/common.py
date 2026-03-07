from pathlib import Path
from requests.exceptions import HTTPError
from typing import List, Dict


data_dir = Path(__file__).parent / 'data'

basic_url: str = 'http://mockedURL/leet.zip'
basic_url2: str = 'http://somewhere/on/the/internet/mod.7z'

git_archive_url: str = 'https://github.com/foo/bar/archive/refs/heads/main.zip'

moddb_start_url: str = 'http://www.moddb.com/addons/start/277404'
moddb_page_info: str = 'https://www.moddb.com/mods/stalker-anomaly/downloads/stalker-anomaly-153'
moddb_mirror_url: str = 'https://www.moddb.com/downloads/mirror/277404/130/926d3b63131d5cabca2b60e9324d0e2f/'


class MockedResponse:
    def __init__(self, status, file: Path, headers: Dict = None) -> None:
        self._status = status
        self._file = file
        self._headers = headers or dict()

    @property
    def status_code(self) -> int:
        return self._status

    @property
    def text(self) -> str:
        return self._file.read_text()

    @property
    def headers(self) -> Dict:
        return self._headers

    def raise_for_status(self) -> None:
        if self._status != 200:
            raise HTTPError('MockedResponse not happy')

    def iter_content(self, *args, **kwargs) -> List[bytes]:
        return [self._file.read_bytes()] if self._file else []


def mocked_get(*args, **kwargs):
    return {
        basic_url: MockedResponse(200, data_dir / 'test.zip'),
        basic_url2: MockedResponse(200, data_dir / 'test.7z'),

        git_archive_url: MockedResponse(200, data_dir / 'test-git-archive.zip'),

        moddb_start_url: MockedResponse(200, data_dir / 'moddb-dl-start.htm'),
        moddb_page_info: MockedResponse(
            200, data_dir / 'moddb-stalker-anomaly-page-minimal.htm'
        ),
        moddb_mirror_url: MockedResponse(
            302, None, headers={'location': basic_url2}
        ),
    }.get(args[0], MockedResponse(404, None))
