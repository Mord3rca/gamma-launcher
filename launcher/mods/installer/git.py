from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Iterator

from launcher.mods.info import ModInfo
from launcher.mods.installer.base import BaseInstaller


class GitResourceInstaller(BaseInstaller):

    def __init__(self, info: ModInfo, find_gamedata: bool = False) -> None:
        super().__init__(info)
        self._find_gamedata = find_gamedata

    @staticmethod
    def _gamedata_iterator(p: Path) -> Iterator[Path]:
        return p.glob('**/gamedata')

    @staticmethod
    def _toplevel_dir_iterator(p: Path) -> Iterator[Path]:
        for i in p.iterdir():
            if i.is_dir():
                yield i

    def install(self, to: Path) -> None:
        print(f'[+] Installing Git Resource mod: {self.info.url}')
        to.mkdir(exist_ok=True)

        iterator = self._gamedata_iterator if self._find_gamedata else self._toplevel_dir_iterator

        with TemporaryDirectory(prefix="gamma-launcher-modinstall-") as dir:
            pdir = Path(dir)
            self.extract(pdir)

            for i in iterator(pdir):
                copytree(i, to / i.name, dirs_exist_ok=True)
