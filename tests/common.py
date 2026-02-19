from pathlib import Path
from requests.exceptions import HTTPError
from typing import List


class MockedResponse:
    def __init__(self, status, file: Path) -> None:
        self._status = status
        self._file = file

    def raise_for_status(self) -> None:
        if self._status != 200:
            raise HTTPError('MockedResponse not happy')

    def iter_content(self, *args, **kwargs) -> List[bytes]:
        return [self._file.read_bytes()] if self._file else []
