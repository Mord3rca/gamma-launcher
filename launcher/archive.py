import os.path

from os import name as os_name
from py7zr import SevenZipFile
from rarfile import RarFile
from typing import List
from zipfile import ZipFile


if os_name == 'nt':
    from os import environ, getenv, pathsep, system

    class Win32ExtractError(Exception):
        pass

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

    def _win32_extract(f: str, p: str) -> None:
        if system(f'7z x -y "-o{p}" "{f}" >nul 2>&1') != 0:
            raise Win32ExtractError(
                f'Error while decompressing with 7z file: {f}\n'
                'Make sure 7z is installed in default path, if not use '
                'LAUNCHER_WIN32_7Z_PATH to set it'
            )

    _extract_func_dict = {
        '7z': _win32_extract,
        'rar': _win32_extract,
        'zip': _win32_extract,
    }
else:
    _extract_func_dict = {
        '7z': lambda f, p: SevenZipFile(f).extractall(p),
        'rar': lambda f, p: RarFile(f).extractall(p),
        'zip': lambda f, p: ZipFile(f).extractall(p),
    }


def extract_archive(filename: str, path: str) -> None:
    ext = os.path.basename(filename).split(os.path.extsep)[-1]
    _extract_func_dict.get(ext)(filename, path)


def list_archive_content(filename: str) -> List[str]:
    ext = os.path.basename(filename).split(os.path.extsep)[-1]
    return {
        '7z': lambda f: SevenZipFile(f).getnames(),
        'rar': lambda f: RarFile(f).namelist(),
        'zip': lambda f: ZipFile(f).namelist(),
    }.get(ext)(filename)
