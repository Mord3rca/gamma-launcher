from pathlib import Path

from launcher.mods.base import Base


class Separator(Base):

    def __init__(self, **kwargs) -> None:
        super().__init__(None, None, kwargs.get('name'))

    def check(self, *args, **kwargs) -> None:
        pass

    def download(self, *args, **kwargs) -> None:
        pass

    def install(self, download_dir: Path, mods_dir: Path) -> None:
        install_dir = mods_dir / self.name

        print(f'[+] Installing separator: {self.name}')
        install_dir.mkdir(exist_ok=True)
        (install_dir / 'meta.ini').write_text(
            '[General]\n'
            'modid=0\n'
            'version=\n'
            'newestVersion=\n'
            'category=0\n'
            'installationFile=\n'
            '\n'
            '[installedFiles]\n'
            'size=0\n'
        )
