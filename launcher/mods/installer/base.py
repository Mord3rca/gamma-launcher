from pathlib import Path
from typing import Optional

from launcher.mods.info import ModInfo
from launcher.mods.downloader import DownloaderFactory


class BaseInstaller:

    def __init__(self, info: ModInfo) -> None:
        self._info = info
        self._dl = DownloaderFactory(info)

    def check(self, dl_dir: Path, update_cache: bool = False) -> None:
        if not self._dl:
            return

        self._dl.check(dl_dir, update_cache)

    def download(self, to: Path, use_cached: bool = False) -> Path:
        if not self._dl:
            raise RuntimeError(
                f'{self.info.name} does not support download() method'
                'since no URL was provided'
            )

        return self._dl.download(to, use_cached)

    def extract(self, to: Path) -> None:
        if not self._dl:
            raise RuntimeError(
                f'{self.info.name} does not support extract() method'
                'since it does not depend on an archive'
            )

        self._dl.extract(to)

    def install(self, to: Path) -> None:
        self.extract(to)

    @property
    def archive(self) -> Path:
        if not self._dl:
            raise RuntimeError(
                f'{self.info.name} does not support archive property'
                'since it does not depend on an archive'
            )

        return self._dl.archive

    @property
    def downloader(self) -> Optional[object]:
        return self._dl

    @property
    def info(self) -> ModInfo:
        return self._info
