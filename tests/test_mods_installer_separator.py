from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from launcher.mods.info import ModInfo
from launcher.mods.installer.separator import SeparatorInstaller


class SeparatorInstallerTestCase(TestCase):

    info: ModInfo = ModInfo({'name': '999 - foo'})

    tempDir: TemporaryDirectory = TemporaryDirectory(prefix='gamma-launcher-separator-installer-tests-')

    def test_install(self) -> None:
        o = SeparatorInstaller(self.info.name)

        pdir = Path(self.tempDir.name)

        o.install(pdir)
        self.assertTrue((pdir / '999 - foo' / 'meta.ini').exists())

    def test_download(self) -> None:
        o = SeparatorInstaller(self.info.name)

        with self.assertRaises(RuntimeError):
            o.download(Path(self.tempDir.name))

    def test_extract(self) -> None:
        o = SeparatorInstaller(self.info.name)

        with self.assertRaises(RuntimeError):
            o.extract(Path(self.tempDir.name))

    def test_archive(self) -> None:
        o = SeparatorInstaller(self.info.name)

        with self.assertRaises(RuntimeError):
            o.archive

    def test_downloader(self) -> None:
        o = SeparatorInstaller(self.info.name)

        self.assertIsNone(o.downloader)

    def test_info(self) -> None:
        o = SeparatorInstaller(self.info.name)

        self.assertEqual(o.info.name, self.info.name)
        self.assertEqual(o.info.author, '')
        self.assertEqual(o.info.title, '')
        self.assertEqual(o.info.url, '')
        self.assertEqual(o.info.iurl, '')
        self.assertIsNone(o.info.subdirs)
        self.assertIsNone(o.info.args)
