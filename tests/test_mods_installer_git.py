from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from common import MockedDownloader

from launcher.mods.info import ModInfo
from launcher.mods.installer.git import GitResourceInstaller


def MockedDLFactory(*args, **kwargs) -> MockedDownloader:
    return MockedDownloader()


class GitResourceInstallerTestCase(TestCase):

    info: ModInfo = ModInfo({
        'name': '1337 - bar',
        'url': 'http://blablabla',
        'iurl': 'not-null',
    })

    tempDir: TemporaryDirectory = TemporaryDirectory(prefix='gamma-launcher-gitresource-installer-tests-')

    @patch('launcher.mods.installer.base.DownloaderFactory', side_effect=MockedDLFactory)
    def test_install(self, _) -> None:
        o = GitResourceInstaller(self.info)
        root = Path(self.tempDir.name) / 'test-install'

        self.assertIsInstance(o.downloader, MockedDownloader)

        root.mkdir()
        o.install(root)

        for i in MockedDownloader._content:
            self.assertTrue((root / i).exists())

    @patch('launcher.mods.installer.base.DownloaderFactory', side_effect=MockedDLFactory)
    def test_install_with_find_gamedata(self, _) -> None:
        o = GitResourceInstaller(self.info, True)
        root = Path(self.tempDir.name) / 'test-install-with-gamedata'

        self.assertIsInstance(o.downloader, MockedDownloader)

        root.mkdir()
        o.install(root)

        for i in MockedDownloader._content:
            if i.parent.name == 'gamedata':
                self.assertTrue((root / 'gamedata' / i.name).exists())

    @patch('launcher.mods.installer.base.DownloaderFactory', side_effect=MockedDLFactory)
    def test_download(self, _) -> None:
        o = GitResourceInstaller(self.info)

        self.assertIsInstance(o.downloader, MockedDownloader)

        self.assertEqual(
            o.download(Path('/lolilolilol')),
            MockedDownloader._file
        )

    def test_info(self) -> None:
        o = GitResourceInstaller(self.info)

        self.assertEqual(o.info, self.info)

    def test_gamedata_iterator(self) -> None:
        root = Path(self.tempDir.name) / 'test-gamedata-iterator'

        gamedatas = [
            root / 'gamedata',
            root / 'subdir' / 'gamedata',
            root / 'subdir' / 'another' / 'gamedata',
        ]

        otherdirs = [
            root / 'fomod',
            root / '001 - Main',
            root / 'bar' / 'foo',
        ]

        # Create tree
        [i.mkdir(parents=True) for i in gamedatas + otherdirs]

        self.assertEqual(
            set(GitResourceInstaller._gamedata_iterator(root)),
            set(gamedatas)
        )

    def test_toplevel_dir_iterator(self) -> None:
        root = Path(self.tempDir.name) / 'test-toplevel-iterator'

        dirs = [
            root / 'foo',
            root / 'foo' / 'bar',

            root / 'leet',

            root / 'main',
            root / 'main' / 'yes',
        ]

        [i.mkdir(parents=True) for i in dirs]

        self.assertEqual(
            set(GitResourceInstaller._toplevel_dir_iterator(root)),
            set(filter(lambda x: x.parent == root, dirs))
        )
