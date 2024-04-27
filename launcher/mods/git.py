from distutils.dir_util import copy_tree
from pathlib import Path
from typing import Set

from launcher.mods.base import Default


class GitInstaller(Default):

    def __init__(self, url: str) -> None:
        super().__init__(**{
            'name': 'Git Installer',
            'url': url,
            'install_directives': None,
            'author': 'Internal',
            'title': f'Git Installer for {url}',
            'info_url': url,
        })
        self.mods = []

    @property
    def url(self) -> str:
        return self._url

    def _find_gamedata(self, pdir: Path, title: str) -> Set[Path]:
        tmp = list(pdir.glob(f"**/{title}"))
        if tmp:
            return set(tmp)

        for i in self.folder_to_install:
            tmp += [v.parent for v in pdir.glob(f"**/{i}")]

        return set(tmp)

    def append(self, **kwargs) -> None:
        self.mods.append(kwargs)

    def check(self, *args, **kwargs) -> None:
        pass

    def install(self, download_dir: Path, mods_dir: Path) -> None:
        if not self._url:
            return

        print(f"[+] Installing Git Mod: {self.url}")
        archive = self.download(download_dir)

        with self.tempDir(archive, prefix="gamma-launcher-modinstall-") as pdir:
            for m in self.mods:
                print(f"  --> Installing {m['name']}")
                install_dir = mods_dir / m["name"]

                iter = self._find_gamedata(pdir, m["title"])
                if not iter:
                    print("  /!\\ Failed to install, directory not found /!\\")
                    continue

                install_dir.mkdir(exist_ok=True)
                for i in iter:
                    for gamedir in self.folder_to_install:
                        pgame_dir = i / gamedir

                        if not pgame_dir.exists():
                            continue

                        copy_tree(
                            str(pgame_dir),
                            str(install_dir / gamedir)
                        )

                self._write_ini_file(install_dir / 'meta.ini', archive, self._url)
