from pathlib import Path


class ModBase:

    def __init__(self, data: dict) -> None:
        self._data = data

    def check(self, dl_dir: Path, update_cache: bool = False) -> None:
        pass

    def download(self, dl_dir: Path, use_cached: bool = False) -> Path:
        pass

    def extract(self, to: Path) -> None:
        pass

    def install(self, to: Path) -> None:
        pass

    @property
    def archive(self) -> Path:
        return None

    @property
    def author(self) -> str:
        return self._data.get('author')

    @property
    def name(self) -> str:
        return self._data.get('name')

    @property
    def title(self) -> str:
        return self._data.get('title')
