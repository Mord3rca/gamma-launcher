from platform import system
from py7zr import SevenZipFile
from subprocess import run
from typing import List
from py7zr.exceptions import UnsupportedCompressionMethodError
from unrar.rarfile import RarFile
from zipfile import ZipFile


def get_mime_from_file(filename) -> str:
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

    raise Exception(f'File {filename} download failed, output is a unknown file type')


if system() == 'Windows':
    class Win32ExtractError(Exception):
        pass

    def _win32_extract(f: str, p: str) -> None:
        if run(['7z', 'x', '-y', f'-o{p}', f], shell=True).returncode != 0:
            raise Win32ExtractError(
                f'Error while decompressing with 7z file: {f}\n'
                'Make sure 7z is installed in default path, if not use '
                'LAUNCHER_WIN32_7Z_PATH to set it'
            )

    _extract_func_dict = {
        'application/x-7z-compressed': _win32_extract,
        'application/x-rar': _win32_extract,
        'application/zip': _win32_extract,
        'application/x-7z-compressed+bcj2': _win32_extract,
    }
else:
    def _7zip_bcj2_workaround(f: str, p: str) -> None:
        if run(['7z', 'x', '-y', f'-o{p}', f]).returncode != 0:
            raise RuntimeError(f'7z error while decompressing {f}')

    def _7zip_extractall(f: str, p: str) -> None:
        try:
            SevenZipFile(f).extractall(p)
        except UnsupportedCompressionMethodError as e:
            print(e.message)
            print("Fallback to 7z binary for extraction.")
            _7zip_bcj2_workaround(f, p)

    _extract_func_dict = {
        'application/x-7z-compressed': _7zip_extractall,
        'application/x-rar': lambda f, p: RarFile(f'{f}').extractall(f'{p}'),
        'application/zip': lambda f, p: ZipFile(f).extractall(p),
        'application/x-7z-compressed+bcj2': _7zip_bcj2_workaround
    }


def extract_archive(filename: str, path: str, mime: str = None) -> None:
    mime = mime or get_mime_from_file(filename)
    _extract_func_dict.get(mime)(filename, path)


def list_archive_content(filename: str, mime: str = None) -> List[str]:
    mime = mime or get_mime_from_file(filename)
    return {
        'application/x-7z-compressed': lambda f: SevenZipFile(f).getnames(),
        'application/x-rar': lambda f: RarFile(f).namelist(),
        'application/zip': lambda f: ZipFile(f).namelist(),
    }.get(mime)(filename)
