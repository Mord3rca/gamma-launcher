from pathlib import Path
from platform import system
from tempfile import TemporaryDirectory
from typing import List
from unittest import mock, TestCase, skipIf

from launcher.archive import extract_archive, get_mime_from_file, list_archive_content

from common import data_dir


class MimeTestCase(TestCase):

    def test_7zip_mime(self):
        mime = get_mime_from_file(str(data_dir / 'test.7z'))

        self.assertEqual(mime, 'application/x-7z-compressed')

    def test_rar_mime(self):
        mime = get_mime_from_file(str(data_dir / 'test.rar'))

        self.assertEqual(mime, 'application/x-rar')

    def test_zip_mime(self):
        mime = get_mime_from_file(str(data_dir / 'test.zip'))

        self.assertEqual(mime, 'application/zip')


class ExtractTestCase(TestCase):

    def _run_extract_test(self, archive: Path) -> None:
        with TemporaryDirectory(prefix='gamma-launcher-archive-extraction-test-') as dir:
            extract_archive(archive, dir)
            self.assertEqual((Path(dir) / 'flag').read_text().strip(), 'success')

    def test_extract_7zip(self):
        self._run_extract_test(data_dir / 'test.7z')

    @skipIf(system() == 'Windows', 'Only make sense on *nix')
    @mock.patch('launcher.archive.SevenZipFile.extractall')
    def test_extract_7zip_bcj2(self, mock_func):
        self._run_extract_test(data_dir / 'test-bcj2-filter.7z')

        self.assertEqual(
            len(mock_func.call_args_list), 0,
            'Decompressing via SevenZipFile was called before BCJ2 workaround'
        )

    def test_extract_rar(self):
        self._run_extract_test(data_dir / 'test.rar')

    def test_extract_zip(self):
        self._run_extract_test(data_dir / 'test.zip')


class ListTestCase(TestCase):

    def _list_archive_test(self, archive: Path, expect: List[str] = ['flag']) -> None:
        members = list_archive_content(str(archive))

        self.assertEqual(members, expect)

    def test_list_7zip(self):
        self._list_archive_test(data_dir / 'test.7z')

    def test_list_rar(self):
        self._list_archive_test(data_dir / 'test.rar')

    def test_list_zip(self):
        self._list_archive_test(data_dir / 'test.zip')

    def test_list_gitlike_archive(self):
        self._list_archive_test(data_dir / 'test-git-archive.zip', [
            'project-main/', 'project-main/flag'
        ])
