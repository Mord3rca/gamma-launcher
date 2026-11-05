from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from launcher.commands.usvfs import Usvfs


class UsvfsTestCase(TestCase):

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory(prefix='gamma-launcher-usvfs-tests-')
        self.root = Path(self._tmp.name)
        self.anomaly = self.root / 'anomaly'
        self.gamma = self.root / 'gamma'
        self.final = self.root / 'final'
        self.mod1 = self.gamma / 'mods' / 'mod1'
        self.mod2 = self.gamma / 'mods' / 'mod2'

        files = {
            self.anomaly / 'bin' / 'AnomalyDX11.exe': 'anomaly-bin',
            self.anomaly / 'gamedata' / 'a.ltx': 'anomaly',
            self.mod1 / 'gamedata' / 'a.ltx': 'mod1',
            self.mod1 / 'gamedata' / 'b.ltx': 'mod1',
            self.mod1 / 'bin' / 'AnomalyDX11.exe': 'mod1-bin',
            self.mod2 / 'gamedata' / 'a.ltx': 'mod2',
            self.gamma / 'profiles' / 'G.A.M.M.A' / 'modlist.txt': '+mod2\n+mod1\n-disabled\n',
        }
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run(self, hardlink: bool) -> None:
        Usvfs().run(Namespace(anomaly=self.anomaly, gamma=self.gamma, final=self.final, hardlink=hardlink))

    def _assert_install(self) -> None:
        self.assertEqual((self.final / 'gamedata' / 'a.ltx').read_text(), 'mod2')
        self.assertEqual((self.final / 'gamedata' / 'b.ltx').read_text(), 'mod1')
        self.assertEqual((self.final / 'bin' / 'AnomalyDX11.exe').read_text(), 'anomaly-bin')
        self.assertEqual((self.mod1 / 'gamedata' / 'a.ltx').read_text(), 'mod1')
        self.assertEqual((self.mod2 / 'gamedata' / 'a.ltx').read_text(), 'mod2')
        self.assertEqual((self.anomaly / 'gamedata' / 'a.ltx').read_text(), 'anomaly')

    def test_copy(self) -> None:
        self._run(hardlink=False)

        self._assert_install()
        self.assertFalse((self.final / 'gamedata' / 'a.ltx').samefile(self.mod2 / 'gamedata' / 'a.ltx'))

    def test_hardlink(self) -> None:
        self._run(hardlink=True)

        self._assert_install()
        self.assertTrue((self.final / 'gamedata' / 'a.ltx').samefile(self.mod2 / 'gamedata' / 'a.ltx'))
        self.assertTrue((self.final / 'gamedata' / 'b.ltx').samefile(self.mod1 / 'gamedata' / 'b.ltx'))
        self.assertTrue((self.final / 'bin' / 'AnomalyDX11.exe').samefile(self.anomaly / 'bin' / 'AnomalyDX11.exe'))

    def test_rerun_keeps_other_files(self) -> None:
        self._run(hardlink=True)
        save = self.final / 'appdata' / 'savedgames' / 'quicksave.scop'
        save.parent.mkdir(parents=True)
        save.write_text('save')

        self._run(hardlink=True)

        self._assert_install()
        self.assertEqual(save.read_text(), 'save')

    def test_copy_over_hardlinks_keeps_sources(self) -> None:
        self._run(hardlink=True)
        self._run(hardlink=False)

        self._assert_install()
