from pathlib import Path
from shutil import copytree
from typing import Set

from launcher.common import folder_to_install
from launcher.mods.installer.default import DefaultInstaller
from launcher.mods.tempfile import DefaultTempDir


class GitInstaller(DefaultInstaller):

    def __init__(self, url: str) -> None:
        super().__init__(**{
            'name': 'Git Installer',
            'url': url,
            'add_dirs': None,
            'author': 'Internal',
            'title': f'Git Installer for {url}',
            'iurl': url,
        })
        self.mods = []

    def _find_gamedata(self, pdir: Path, title: str) -> Set[Path]:
        tmp = list(pdir.glob(f"**/{title}"))
        if tmp:
            return set(tmp)

        for i in folder_to_install:
            tmp += [v.parent for v in pdir.glob(f"**/{i}")]

        return sorted(set(tmp))

    def append(self, **kwargs) -> None:
        self.mods.append(kwargs)

    def install(self, to: Path) -> None:
        if not self.url:
            return

        print(f"[+] Installing Git Mod: {self.url}")

        with DefaultTempDir(self, prefix="gamma-launcher-modinstall-") as pdir:
            for m in self.mods:
                print(f"  --> Installing {m['name']}")
                install_dir = to / m["name"]

                iter = self._find_gamedata(pdir, m["title"])
                if not iter:
                    print("  /!\\ Failed to install, directory not found /!\\")
                    continue

                install_dir.mkdir(exist_ok=True)
                for i in iter:
                    for gamedir in folder_to_install:
                        pgame_dir = i / gamedir

                        if not pgame_dir.exists():
                            continue

                        copytree(pgame_dir, install_dir / gamedir, dirs_exist_ok=True)

                self._write_ini_file(install_dir / 'meta.ini')
