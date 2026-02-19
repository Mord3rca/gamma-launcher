from pathlib import Path
from requests.exceptions import HTTPError
from typing import List, Dict


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
