from hashlib import md5
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from shutil import copy

from common import data_dir
from launcher.userltx import UserLTX


class UserLTXTestCase(TestCase):

    ltx_test_file: Path = data_dir / 'user.ltx'
    ltx_test_file_digest: str = '61b4afe9293a4d63ed42257191b500e2'

    tempDir: TemporaryDirectory = TemporaryDirectory(prefix='gamma-launcher-userltx-tests-')

    def test_edit(self) -> None:
        u = UserLTX(self.ltx_test_file)

        u['ai_use_torch_dynamic_lights'] = 'off'
        u['bind_sec inventory'] = 'kESC'

        tfile = Path(self.tempDir.name) / 'test-edit.ltx'
        u.save(tfile)

        self.assertTrue(tfile.exists())

    def test_edit_with_context(self) -> None:
        tfile = Path(self.tempDir.name) / 'test-edit-with-context.ltx'
        copy(self.ltx_test_file, tfile)

        with UserLTX(tfile) as cfg:
            cfg['r_screenshot_mode'] = 'jpg'

        self.assertEqual(md5(tfile.read_bytes()).hexdigest(), 'f8879f55d01cc00538d9784a4b2346db')

    def test_copy(self) -> None:
        u = UserLTX(self.ltx_test_file)

        tfile = Path(self.tempDir.name) / 'test-copy.ltx'
        u.save(tfile)

        self.assertEqual(md5(tfile.read_bytes()).hexdigest(), self.ltx_test_file_digest)

    def test_read(self) -> None:
        u = UserLTX(self.ltx_test_file)

        self.assertEqual(u['ai_aim_min_angle'], '0.19635')
        self.assertEqual(u['ai_use_torch_dynamic_lights'], 'on')
        self.assertEqual(u['default_controls'], '')
        self.assertEqual(u['bind left'], 'kLEFT')
        self.assertEqual(u['bind jump'], 'kSPACE')
        self.assertEqual(u['bind crouch'], 'kLCONTROL')
        self.assertEqual(u['bind inventory'], 'kI')
        self.assertEqual(u['bind_sec inventory'], 'kTAB')
        self.assertEqual(u['dsr_test'], '(0.000000, 0.000000, 0.000000)')
        self.assertEqual(u['g_dead_body_collision'], 'actor_only')
        self.assertEqual(u['g_game_difficulty'], 'gd_novice')
        self.assertEqual(u['r_screenshot_mode'], 'png')
        self.assertEqual(u['rs_screenmode'], 'borderless')
        self.assertEqual(u['vid_mode'], '1920x1080')

    def test_write(self) -> None:
        u = UserLTX()

        u['key1'] = 'foo'
        u['key2'] = 'bar'

        tfile = Path(self.tempDir.name) / 'test-write.ltx'
        u.save(tfile)

        self.assertTrue(tfile.exists())
        self.assertEqual(md5(tfile.read_bytes()).hexdigest(), 'c5127d3806debb427bce1c0d6a576929')
