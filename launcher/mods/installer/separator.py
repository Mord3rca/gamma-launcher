from pathlib import Path

from launcher.mods.base import ModBase


class SeparatorInstaller(ModBase):

    def __init__(self, name: str) -> None:
        super().__init__(None, name, None)

    def install(self, to: Path) -> None:
        install_dir = to / self.name

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
