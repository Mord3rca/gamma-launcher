from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from launcher.mods.downloader.moddb import ModDBDownloader

from common import MockedResponse


data_dir: Path = Path(__file__).parent / 'data'


def mocked_get(*args, **kwargs):
    return {
        ModDBDownloaderTestCase._dl_start_url: MockedResponse(200, data_dir / 'moddb-dl-start.htm'),
        ModDBDownloaderTestCase._dl_mirror_url: MockedResponse(
            302, None, headers={'location': ModDBDownloaderTestCase._dl_url}
        ),
        ModDBDownloaderTestCase._mod_page_info: MockedResponse(
            200, data_dir / 'moddb-stalker-anomaly-page-minimal.htm'
        ),
        ModDBDownloaderTestCase._dl_url: MockedResponse(200, data_dir / 'test.7z'),
    }.get(args[0], MockedResponse(404, None))


class ModDBDownloaderTestCase(TestCase):

    _dl_url: str = 'http://somewhere/on/the/internet/mod.7z'
    _dl_start_url: str = 'http://www.moddb.com/addons/start/277404'
    _dl_mirror_url: str = 'https://www.moddb.com/downloads/mirror/277404/130/926d3b63131d5cabca2b60e9324d0e2f/'
    _mod_page_info: str = 'https://www.moddb.com/mods/stalker-anomaly/downloads/stalker-anomaly-153'

    @patch('launcher.mods.downloader.moddb.g_session.get', side_effect=mocked_get)
    def test_get_download_url(self, mock_request) -> None:
        self.assertEqual(ModDBDownloader._get_download_url(self._dl_start_url), self._dl_url)

        self.assertEqual(len(mock_request.call_args_list), 2)
        self.assertTrue(mock_request.call_args_list[0].called_with(self._dl_start_url))
        self.assertTrue(mock_request.call_args_list[1].called_with(self._dl_mirror_url))

    @patch('launcher.mods.downloader.moddb.g_session.get', side_effect=mocked_get)
    def test_parse_moddb_data(self, mock_request) -> None:
        o = ModDBDownloader._parse_moddb_data(self._mod_page_info)

        self.assertEqual(o['Filename'], 'Anomaly-1.5.3-Full.2.7z')
        self.assertEqual(o['MD5 Hash'], 'd6bce51a4e6d98f9610ef0aa967ba964')
        self.assertEqual(o['Download'], 'https://www.moddb.com/downloads/start/277404')

        mock_request.assert_called_once_with(self._mod_page_info)

    @patch('launcher.mods.downloader.moddb.g_session.get', side_effect=mocked_get)
    def test_download(self, mock_request) -> None:
        o = ModDBDownloader(self._dl_start_url, self._mod_page_info)

        # TODO: Better test cases (check cache, reqouests call, ...)
        with TemporaryDirectory(prefix='gamma-launcher-moddb-downloader-test-') as dir:
            pdir = Path(dir)

            o.download(pdir)
            self.assertTrue((pdir / 'mod.7z').exists())
