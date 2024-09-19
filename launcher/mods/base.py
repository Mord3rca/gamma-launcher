from pathlib import Path


class ModBase:

    def __init__(self, author: str, name: str, title: str, *args) -> None:
        self._name = name
        self._title = title
        self._author = author

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
        return self._author

    @property
    def name(self) -> str:
        return self._name

    @property
    def title(self) -> str:
        return self._title
