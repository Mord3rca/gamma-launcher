from pathlib import Path
from platform import system
from tempfile import TemporaryDirectory
from typing import Callable

from launcher.common import folder_to_install


class HotfixPathCase:

    def _post_decompression_hotfix_fix_path_case(self, dir: Path) -> None:
        for path in filter(
            lambda x: x.name.lower() in folder_to_install and x.name != x.name.lower(),
            dir.glob('**')
        ):
            for file in path.glob('**/*.*'):
                t = file.relative_to(path.parent)
                rp = str(t.parent).lower()
                nfolder = path.parent / rp
                nfolder.mkdir(parents=True, exist_ok=True)
                file.rename(nfolder / file.name)


class HotfixMalformedArchive:

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


tempDirHotfixes = (HotfixPathCase, HotfixMalformedArchive) if not system() == 'Windows' else ()


class DefaultTempDir(TemporaryDirectory, *tempDirHotfixes):

    def __init__(self, extract_func: Callable[[Path], None], *args, **kwargs) -> None:
        TemporaryDirectory.__init__(self, *args, **kwargs)
        self._extract_func = extract_func

    def __enter__(self) -> Path:
        s = Path(TemporaryDirectory.__enter__(self))
        self._extract_func(s)
        for hotfix in sorted(filter(lambda x: 'hotfix' in x, dir(self))):
            getattr(self, hotfix)(s)
        return s
