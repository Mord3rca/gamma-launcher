import os.path

from rarfile import RarFile
from py7zr import SevenZipFile
from zipfile import ZipFile


def extract_archive(filename: str, path: str) -> None:
    ext = os.path.basename(filename).split(os.path.extsep)[-1]
    {
        '7z': lambda f, p: SevenZipFile(f).extractall(p),
        'rar': lambda f, p: RarFile(f).extractall(p),
        'zip': lambda f, p: ZipFile(f).extractall(p),
    }.get(ext)(filename, path)


def list_archive_content(filename: str):
    ext = os.path.basename(filename).split(os.path.extsep)[-1]
    return {
        '7z': lambda f: SevenZipFile(f).getnames(),
        'rar': lambda f: RarFile(f).namelist(),
        'zip': lambda f: ZipFile(f).namelist(),
    }.get(ext)(filename)
