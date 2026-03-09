from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from launcher.mods.info import ModInfo
from launcher.mods.installer.base import BaseInstaller


class MockedDownloader:

    @property
    def archive(self, *args, **kwargs):
        return Path('/void')

    def check(self, *args, **kwargs):
        pass

    def download(self, *args, **kwargs):
        pass

    def extract(self, to: Path):
        (to / 'flag').write_text('YES')


def mocked_downloader_factory(info: ModInfo, *args, **kwargs):
    return MockedDownloader() if info.url else None


class BaseInstallerTestCase(TestCase):

    info: ModInfo = ModInfo({'name': '001 - foo'})

    info_with_url: ModInfo = ModInfo({'name': '005 - bar', 'url': 'something'})

    tempDir: TemporaryDirectory = TemporaryDirectory(prefix='gamma-launcher-base-installer-tests-')

    @patch('launcher.mods.installer.base.DownloaderFactory', side_effect=mocked_downloader_factory)
    def test_no_downloader(self, _) -> None:
        o = BaseInstaller(self.info)

        self.assertIsNone(o.downloader)

        # Will except in case of error
        o.check(Path('/this/path/does/not/exist'))

        with self.assertRaises(RuntimeError):
            o.archive

        with self.assertRaises(RuntimeError):
            o.download(Path('/this/path/dont/exist'))

        with self.assertRaises(RuntimeError):
            o.extract(Path('/this/path/dont/exist'))

        with self.assertRaises(RuntimeError):
            o.install(Path('/this/path/dont/exist'))

    @patch('launcher.mods.installer.base.DownloaderFactory', side_effect=mocked_downloader_factory)
    def test_with_mocked_downloader(self, _) -> None:
        o = BaseInstaller(self.info_with_url)
        pdir = Path(self.tempDir.name)
        flag = pdir / 'flag'

        self.assertIsInstance(o.downloader, MockedDownloader)

        # Will do nothing
        o.check(Path('/this/path/does/not/exist'))

        self.assertEqual(o.archive, Path('/void'))

        o.download(Path('/this/path/dont/exist'))

        o.extract(pdir)
        self.assertTrue(flag.exists())
        self.assertTrue(flag.read_text() == 'YES')

        flag.unlink()

        o.install(pdir)
        self.assertTrue(flag.exists())
        self.assertTrue(flag.read_text() == 'YES')
