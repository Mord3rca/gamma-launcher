import os
import sys
from subprocess import run
from shutil import which
from typing import List
from unrar.rarfile import RarFile
from zipfile import ZipFile


# --- Dependency Checks ---
def check_dependencies() -> None:
    """Ensure required external tools are available before running."""
    missing = []
    if which('7z') is None:
        missing.append("7z (system 7z / p7zip must be installed)")
    if which('unrar') is None:
        missing.append("unrar (needed for RAR extraction)")

    if missing:
        print("=== MISSING DEPENDENCIES ===")
        for dep in missing:
            print(f" - {dep}")
        print("These tools are required for archive handling.\n"
              "Install them and try again.")
        sys.exit(1)


check_dependencies()


def get_mime_from_file(filename: str) -> str:
    """Detect archive type based on magic bytes."""
    with open(str(filename), 'rb') as f:
        header = f.read(16)

    signatures = {
        b'PK\x03\x04': 'application/zip',
        b'Rar': 'application/x-rar',
        b'\x37\x7A\xBC\xAF\x27\x1C': 'application/x-7z-compressed',
    }

    for sig, mime in signatures.items():
        if header.startswith(sig):
            return mime

    raise Exception(f"File {filename} has unknown or unsupported archive type")


def _system_7z_extract(archive: str, dest: str) -> None:
    """Extract 7z archive using system 7z."""
    print(f"Extracting {os.path.basename(archive)} with system 7z...")
    result = run(['7z', 'x', '-y', f'-o{dest}', str(archive)],
                 capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(f"7z extraction failed for {archive}")
    print(f"Extraction complete: {os.path.basename(archive)}")


def _system_7z_list(archive: str) -> List[str]:
    """List contents of a 7z archive using system 7z."""
    result = run(['7z', 'l', '-slt', str(archive)],
                 capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(f"Cannot list 7z archive contents: {archive}")

    filenames = []
    for line in result.stdout.splitlines():
        if line.startswith('Path = '):
            path = line.replace('Path = ', '').strip()
            if path:
                filenames.append(path)
    return filenames


def _rar_extract(f: str, p: str) -> None:
    """Extract RAR archive using unrar library."""
    RarFile(str(f)).extractall(str(p))


# --- Extraction function mapping ---
_extract_func_dict = {
    'application/x-7z-compressed': _system_7z_extract,
    'application/x-rar': _rar_extract,
    'application/zip': lambda f, p: ZipFile(str(f)).extractall(str(p)),
}


def extract_archive(filename: str, path: str, mime: str = None) -> None:
    """Extract an archive to the given path."""
    mime = mime or get_mime_from_file(filename)
    print(f"=== EXTRACTING: {os.path.basename(filename)} ===")
    print(f"MIME type: {mime}")
    print(f"Destination: {path}")
    func = _extract_func_dict.get(mime)
    if func is None:
        raise Exception(f"No extraction method for MIME type: {mime}")
    func(filename, path)
    print(f"=== EXTRACTION COMPLETE ===\n")


def list_archive_content(filename: str, mime: str = None) -> List[str]:
    """List contents of an archive without extracting it."""
    mime = mime or get_mime_from_file(filename)

    if mime == 'application/x-7z-compressed':
        return _system_7z_list(filename)

    return {
        'application/x-rar': lambda f: RarFile(str(f)).namelist(),
        'application/zip': lambda f: ZipFile(str(f)).namelist(),
    }.get(mime)(filename)