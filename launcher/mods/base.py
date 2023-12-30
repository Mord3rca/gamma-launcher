from abc import ABC, abstractmethod
from distutils.dir_util import copy_tree
from pathlib import Path
from tempfile import TemporaryDirectory
from os import name as os_name
from typing import List

from launcher.archive import extract_archive
from launcher.downloader import download_archive, HashError
from launcher.downloader.moddb import parse_moddb_data
from launcher.hash import check_hash
from launcher.meta import create_ini_file


class CheckHashError(Exception):
    pass


class Base(ABC):

    def __init__(self, author: str, title: str, name: str) -> None:
        self._author = author
        self._title = title
        self._name = name

    @property
    def author(self) -> str:
        return self._author

    @property
    def title(self) -> str:
        return self._title

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def check(self) -> None:
        pass

    @abstractmethod
    def download(self) -> Path:
        pass

    @abstractmethod
    def install(self, download_dir: Path, mods_dir: Path) -> None:
        pass


class Default(Base):

    folder_to_install: List[str] = ['appdata', 'bin', 'db', 'gamedata']

    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs.get('author'), kwargs.get('title'), kwargs.get('name'))
        self._url = kwargs.get('url')
        self._info_url = kwargs.get('info_url', None)
        self._install_directives = kwargs.get('install_directives', None)

    def _check_with_update(self, file: Path, info: dict, dl_dir: Path, hash: str) -> None:
        try:
            download_archive(self._url, dl_dir, use_cached=True, hash=hash)
        except ConnectionError as e:
            raise CheckHashError(f'Failed to redownload {file.name}\n  -> {e}')
        except HashError:
            raise CheckHashError(f'{file.name} failed MD5 check after being redownloaded')

    def _check_without_update(self, file: Path, info: dict, dl_dir: Path, hash: str) -> None:
        if not file.exists():
            raise CheckHashError(f"{file.name} not found on disk")

        if check_hash(file, hash):
            return

        raise CheckHashError(f"{file.name} MD5 missmatch")

    def check(self, dl_dir: Path, update_cache: bool = False, *args, **kwargs) -> None:
        if not self._info_url:
            raise CheckHashError(f'No info_url related to {self.name} mod')

        try:
            info = parse_moddb_data(self._info_url)
            file = dl_dir / info['Filename']
            hash = info['MD5 Hash']
        except ConnectionError as e:
            raise CheckHashError(f'Error while fetching moddb page for {self._info_url}\n  -> {e}')
        except KeyError:
            raise CheckHashError(f'Error while parsing moddb page for {self._info_url}')

        if info.get('Download', '') not in self._url:
            raise CheckHashError(f'Skipping {file.name} since ModDB info do not match download url')

        (self._check_with_update if update_cache else self._check_without_update)(file, info, dl_dir, hash)

    def download(self, mod_dir: Path) -> Path:
        return download_archive(self._url, mod_dir)

    def _fix_path_case(self, dir: Path) -> None:
        # Do not exec this on windows
        if os_name == 'nt':
            return

        for path in filter(
            lambda x: x.name.lower() in self.folder_to_install and x.name != x.name.lower(),
            dir.glob('**')
        ):
            for file in path.glob('**/*.*'):
                t = file.relative_to(path.parent)
                rp = str(t.parent).lower()
                nfolder = path.parent / rp
                nfolder.mkdir(parents=True, exist_ok=True)
                file.rename(nfolder / file.name)

    def _fix_malformed_archive(self, dir: Path) -> None:
        # Do not exec this on windows
        if os_name == 'nt':
            return

        for path in dir.glob('*.*'):
            if '\\' not in path.name:
                continue

            p = dir / path.name.replace('\\', '/')
            p.parent.mkdir(parents=True, exist_ok=True)
            path.rename(dir / p)

    def install(self, download_dir: Path, mods_dir: Path) -> None:
        install_dir = mods_dir / self.name

        print(f'[+] Installing mod: {self.title}')
        archive = self.download(download_dir)

        install_dir.mkdir(exist_ok=True)

        with TemporaryDirectory(prefix="gamma-launcher-modinstall-") as dir:
            pdir = Path(dir)
            extract_archive(archive, dir)
            self._fix_malformed_archive(pdir)
            self._fix_path_case(pdir)

            iterator = [pdir] + ([Path(dir) / i for i in self._install_directives] if self._install_directives else [])
            for i in iterator:
                if pdir != i:
                    print(f'    Installing {i.name} -> {install_dir}')

                if not i.exists():
                    print(f'    WARNING: {i.name} does not exist')

                # Well, I guess it's a feature now.
                # Maybe I'm not that lazy after all
                for gamedir in self.folder_to_install:
                    pgame_dir = i / gamedir

                    if not pgame_dir.exists():
                        continue

                    copy_tree(
                        str(pgame_dir),
                        str(install_dir / gamedir)
                    )

        create_ini_file(install_dir / 'meta.ini', archive.name, self._info_url or self._url)
