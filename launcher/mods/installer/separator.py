from pathlib import Path

from launcher.mods.info import ModInfo
from launcher.mods.installer.base import BaseInstaller


class SeparatorInstaller(BaseInstaller):

    def __init__(self, name: str) -> None:
        super().__init__(ModInfo({'name': name}))

    def install(self, to: Path) -> None:
        install_dir = to / self.info.name

        print(f'[+] Installing separator: {self.info.name}')
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
