from distutils.dir_util import copy_tree
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Set

from launcher.archive import extract_archive
from launcher.mods.base import Default


class GammaLargeFile(Default):

    def __init__(self, url: str) -> None:
        super().__init__(**{
            'name': 'Gamma Large File Installer',
            'url': url,
            'install_directives': None,
            'author': 'Internal',
            'title': 'Gamma Large File Installer',
            'info_url': url,
        })
        self.mods = []

    def _find_gamedata(self, pdir: Path, title: str) -> Set[Path]:
        if (pdir / "gamma_large_files_v2-main" / title).exists():
            return {(pdir / "gamma_large_files_v2-main" / title)}

        return {}

    def append(self, **kwargs) -> None:
        self.mods.append(kwargs)

    def check(self, *args, **kwargs) -> None:
        pass

    def install(self, download_dir: Path, mods_dir: Path) -> None:
        if not self._url:
            return

        print("[+] Installing G.A.M.M.A. Large Files v2")
        archive = self.download(download_dir)

        with TemporaryDirectory(prefix="gamma-launcher-modinstall-") as dir:
            pdir = Path(dir)
            extract_archive(archive, dir)
            self._fix_malformed_archive(pdir)
            self._fix_path_case(pdir)

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
