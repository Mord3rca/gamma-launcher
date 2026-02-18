from unittest import TestCase
from pathlib import Path
from typing import Dict

from launcher.hash import check_hash


data_dir = Path(__file__).parent / 'data'


class CheckHashTestCase(TestCase):

    _files: Dict[Path, str] = {
        data_dir / 'test.7z': 'ca907780e6db0343fe2ea663739b27b3',
        data_dir / 'test-bcj2-filter.7z': '86c495417504238a5411283ea6cdd46d',
        data_dir / 'test-git-archive.zip': 'cf7618fe2430b2ea3652dc773288e5aa',
        data_dir / 'test.rar': '37654f57366a85bf54967897f44f809f',
        data_dir / 'test.zip': '26134043be9927512a7e47f2e4261605',
    }

    def test_all_checksum(self):
        for file, checksum in self._files.items():
            self.assertTrue(check_hash(file, checksum))
