from pathlib import Path
from platform import system
from tempfile import TemporaryDirectory

from launcher.common import folder_to_install
from launcher.mods import ModBase


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

    def __init__(self, mod: ModBase, **kwargs) -> None:
        TemporaryDirectory.__init__(self, **kwargs)
        self._mod = mod

    def __enter__(self) -> Path:
        s = Path(TemporaryDirectory.__enter__(self))
        self._mod.extract(s, tmpdir=s)
        for hotfix in sorted(filter(lambda x: 'hotfix' in x, dir(self))):
            getattr(self, hotfix)(s)
        return s
