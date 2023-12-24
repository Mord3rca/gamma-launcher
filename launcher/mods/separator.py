from pathlib import Path

from launcher.meta import create_ini_separator_file
from launcher.mods.base import Base


class Separator(Base):

    def __init__(self, **kwargs) -> None:
        super().__init__(None, None, kwargs.get('name'))

    def download(self, *args, **kwargs) -> None:
        pass

    def install(self, download_dir: Path, mods_dir: Path) -> None:
        install_dir = mods_dir / self.name

        print(f'[+] Installing separator: {self.name}')
        install_dir.mkdir(exist_ok=True)
        create_ini_separator_file(install_dir / 'meta.ini')
