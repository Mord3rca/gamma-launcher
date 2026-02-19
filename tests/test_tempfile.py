from unittest import TestCase, skipIf
from platform import system
from pathlib import Path

from launcher.archive import extract_archive
from launcher.tempfile import DefaultTempDir

from common import data_dir


@skipIf(system() == 'Windows', 'Only make sense on *nix')
class DefaultTempDirTestCase(TestCase):

    def _decompress_and_check(self, file: Path, flagname: str = 'flag.txt') -> None:
        with DefaultTempDir(
            lambda x: extract_archive(file, x),
            prefix='gamma-launcher-tempdir-test-'
        ) as pdir:
            self.assertEqual(
                (pdir / 'gamedata' / 'scripts' / flagname).read_text().strip(),
                'success'
            )

    def test_fix_path_malformed_only(self) -> None:
        self._decompress_and_check(data_dir / 'test-malformed-path.7z')

    def test_fix_path_case_only(self) -> None:
        self._decompress_and_check(data_dir / 'test-malformed-case.7z', 'flag.TXT')

    def test_fix_path_and_case(self) -> None:
        self._decompress_and_check(data_dir / 'test-malformed-both.7z', 'FLAG.txt')
