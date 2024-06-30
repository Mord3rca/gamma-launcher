from distutils.dir_util import copy_tree
from git import Repo
from pathlib import Path
from tempfile import TemporaryDirectory

from os import getenv, name as os_name
from shutil import rmtree
from subprocess import run
from py7zr import SevenZipFile
from rarfile import RarFile
from typing import List
from zipfile import ZipFile


class SevenZipDecompressionError(Exception):
    pass


def get_mime_from_file(filename: Path) -> str:
    # Yup ... It's a hack.
    if (filename / 'HEAD').is_file():
        return 'application/x-git'

    with open(filename, 'rb') as f:
        d = f.read(16)

    mimes = {
        'application/zip': lambda d: d[:4] == b'PK\x03\x04',
        'application/x-rar': lambda d: d[:3] == b'Rar',
        'application/x-7z-compressed': lambda d: d[:6] == b'\x37\x7A\xBC\xAF\x27\x1C',
    }

    for n, f in mimes.items():
        if f(d):
            return n

    return 'Unknown'


def _7zip_extract(f: str, p: str) -> None:
    if run(['7z', 'x', '-y', f'-o{p}', f]).returncode != 0:
        raise SevenZipDecompressionError(f'7z error will decompressing {f}')


def clone_git_reference(archive: Path, dest: Path) -> None:
    with TemporaryDirectory(prefix='gamma-launcher-git-extract-') as dir:
        p = Path(dir)
        Repo.clone_from(f'file://{archive}', p, depth=1, reference=p)
        rmtree(p / '.git')
        copy_tree(str(p), str(dest))


if os_name == 'nt':
    from os import environ, pathsep

    # Adding default 7-Zip path or user defined to PATH
    if getenv('LAUNCHER_WIN32_7Z_PATH'):
        environ['PATH'] += pathsep + getenv('LAUNCHER_WIN32_7Z_PATH')
    else:
        environ['PATH'] += pathsep + pathsep.join(
            {
                'C:\\Program Files\\7-Zip',
                'C:\\Program Files (x86)\\7-Zip',
            }
        )

    _extract_func_dict = {
        'application/x-7z-compressed': _7zip_extract,
        'application/x-rar': _7zip_extract,
        'application/zip': _7zip_extract,
        'application/x-7z-compressed+bcj2': _7zip_extract,
        'application/x-git': clone_git_reference,
    }
else:
    _extract_func_dict = {
        'application/x-7z-compressed': lambda f, p: SevenZipFile(f).extractall(p),
        'application/x-rar':
        _7zip_extract if getenv('GAMMA_LAUNCHER_USE_RARFILE', None) is None else
        lambda f, p: RarFile(f).extractall(p),
        'application/zip': lambda f, p: ZipFile(f).extractall(p),
        'application/x-7z-compressed+bcj2': _7zip_extract,
        'application/x-git': clone_git_reference,
    }


def extract_archive(filename: Path, path: str, mime: str = None) -> None:
    mime = mime or get_mime_from_file(filename)
    _extract_func_dict.get(mime)(filename, path)


def list_archive_content(filename: Path, mime: str = None) -> List[str]:
    mime = mime or get_mime_from_file(filename)
    return {
        'application/x-7z-compressed': lambda f: SevenZipFile(f).getnames(),
        'application/x-rar': lambda f: RarFile(f).namelist(),
        'application/zip': lambda f: ZipFile(f).namelist(),
    }.get(mime)(filename)


def extract_git_archive(archive: Path, dest: Path, glob: str = '*') -> None:
    with TemporaryDirectory(prefix='gamma-launcher-github-extract-') as dir:
        pdir = Path(dir)
        extract_archive(archive, dir)
        copy_tree(
            str(list(pdir.glob(glob))[0]),
            str(dest)
        )
