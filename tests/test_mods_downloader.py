from unittest import TestCase

from launcher.mods.info import ModInfo
from launcher.mods.downloader import DefaultDownloader, DownloaderFactory, GithubDownloader, ModDBDownloader


class DownloaderFactoryTestCase(TestCase):

    _info_moddb = ModInfo({'url': 'https://moddb.com/addons/start/1337'})

    _info_git1 = ModInfo({'url': 'https://github.com/Mord3rca/gamma-launcher'})
    _info_git2 = ModInfo({'url': 'https://github.com/Mord3rca/gamma-launcher/archive/refs/heads/master.zip'})

    _random_archive = ModInfo({'url': 'https://somewhere/on/the/internet.rar'})

    _info_with_args = ModInfo({'url': 'https://somewhere/on/the/internet.rar', 'args': ('hello.rar', 'HASH')})

    _info_none = ModInfo({})

    def test_moddb_url(self):
        o = DownloaderFactory(self._info_moddb)
        self.assertIsInstance(o, ModDBDownloader)

    def test_git_url(self):
        o = DownloaderFactory(self._info_git1)
        self.assertIsInstance(o, GithubDownloader)

        o = DownloaderFactory(self._info_git2)
        self.assertIsInstance(o, DefaultDownloader)

    def test_random_archive(self):
        o = DownloaderFactory(self._random_archive)
        self.assertIsInstance(o, DefaultDownloader)

    def test_none_url(self):
        o = DownloaderFactory(self._info_none)
        self.assertIsNone(o)

    def test_default_with_args(self):
        o = DownloaderFactory(self._info_with_args)
        self.assertIsInstance(o, DefaultDownloader)
