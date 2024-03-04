from distutils.dir_util import copy_tree
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Set

from launcher.archive import extract_archive
from launcher.mods.base import Default


class GammaLargeFile(Default):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._url = kwargs.get('info_url', None)

    def _find_gamedata(self, pdir: Path) -> Set[Path]:
        if (pdir / "gamma_large_files_v2-main" / self._title).exists():
            return {(pdir / "gamma_large_files_v2-main" / self._title)}

        tmp = []
        for i in self.folder_to_install:
            tmp += [v.parent for v in pdir.glob(f'**/{i}')]

        return set(tmp)

    def check(self, *args, **kwargs) -> None:
        pass

    def install(self, download_dir: Path, mods_dir: Path) -> None:
        if not self._url:
            return
        install_dir = mods_dir / self.name

        print(f'[+] Installing GAMMA large File: {self.title}')
        archive = self.download(download_dir)

        install_dir.mkdir(exist_ok=True)

        with TemporaryDirectory(prefix="gamma-launcher-modinstall-") as dir:
            pdir = Path(dir)
            extract_archive(archive, dir)
            self._fix_malformed_archive(pdir)
            self._fix_path_case(pdir)

            for i in self._find_gamedata(pdir):
                for gamedir in self.folder_to_install:
                    pgame_dir = i / gamedir

                    if not pgame_dir.exists():
                        continue

                    copy_tree(
                        str(pgame_dir),
                        str(install_dir / gamedir)
                    )

        self._write_ini_file(install_dir / 'meta.ini', archive, self._info_url or self._url)
