from pathlib import Path
from typing import Optional


class ModBase:

    def __init__(self, author: Optional[str], name: str, title: Optional[str], *args) -> None:
        self._name = name
        self._title = title
        self._author = author

    def check(self, dl_dir: Path, update_cache: bool = False) -> bool:
        return True

    def download(self, to: Path, use_cached: bool = False, **kwargs) -> Path:
        raise NotImplementedError

    def extract(self, to: Path, **kwargs) -> None:
        pass

    def revision(self) -> Optional[str]:
        return None

    def install(self, to: Path) -> None:
        pass

    @property
    def archive(self) -> Optional[Path]:
        return None

    @property
    def author(self) -> Optional[str]:
        return self._author

    @property
    def name(self) -> str:
        return self._name

    @property
    def title(self) -> Optional[str]:
        return self._title
