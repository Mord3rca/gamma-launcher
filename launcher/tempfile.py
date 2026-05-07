from pathlib import Path
from platform import system
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Callable
import tempfile as _tempfile_mod

from launcher.common import folder_to_install


class HotfixPathCase:
    """Class adding a method to `DefaultTempDir` object to fix
    path case of files contained in temporary directory
    """

    def _post_decompression_hotfix_fix_path_case(self, dir: Path) -> None:
        for path in filter(
            lambda x: x.name.lower() in folder_to_install and x.name != x.name.lower(),
            dir.glob('**')
        ):
            for file in path.glob('**/*.*'):
                t = file.relative_to(path.parent)
                rp = str(t.parent).lower()  # TODO: Check if lowering filename too will be OK
                nfolder = path.parent / rp
                nfolder.mkdir(parents=True, exist_ok=True)
                file.rename(nfolder / file.name)


class HotfixMalformedArchive:
    """Class adding a method to `DefaultTempDir` object to fix
    path separator of files contained in temporary directory
    """

    def _post_decompression_hotfix_00_malformed_archive(self, dir: Path) -> None:
        for path in dir.glob('*.*'):
            if '\\' not in path.name:
                continue
            # Probably a directory
            if path.stat().st_size == 0:
                continue

            p = dir / path.name.replace('\\', '/')
            p.parent.mkdir(parents=True, exist_ok=True)
            path.rename(dir / p)

@contextmanager
def scoped_tempdir(base_dir: str):
    """Context manager that redirects tempfile to a directory under *base_dir*.

    Creates ``<base_dir>/.tmp`` if needed, sets ``tempfile.tempdir``
    to it for the duration of the block, and restores the previous value on exit.

    This avoids filling a small tmpfs (e.g. /tmp) during large extractions.

    Argument(s):
    * base_dir -- Root directory; temp files go in ``<base_dir>/.tmp``
    """
    tmp_path = Path(base_dir) / ".tmp"
    tmp_path.mkdir(parents=True, exist_ok=True)
    old = _tempfile_mod.tempdir
    try:
        _tempfile_mod.tempdir = str(tmp_path)
        yield tmp_path
    finally:
        _tempfile_mod.tempdir = old


tempDirHotfixes = (HotfixPathCase, HotfixMalformedArchive) if not system() == 'Windows' else ()
"List of hotfixes added to `DefaultTempDir`"


class DefaultTempDir(TemporaryDirectory, *tempDirHotfixes):
    """A `tempfile.TemporaryDirectory` specialization to apply hotpatches to content
    Argument(s)
    * extract_func -- A callable used to execute an action before
    executing hotpatch method registered in this class
    """

    def __init__(self, extract_func: Callable[[Path], None], *args, **kwargs) -> None:
        TemporaryDirectory.__init__(self, *args, **kwargs)
        self._extract_func = extract_func

    def __enter__(self) -> Path:
        s = Path(TemporaryDirectory.__enter__(self))
        self._extract_func(s)
        for hotfix in sorted(filter(lambda x: 'hotfix' in x, dir(self))):
            getattr(self, hotfix)(s)
        return s
