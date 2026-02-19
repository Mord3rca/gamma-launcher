from hashlib import md5
from requests.exceptions import ConnectionError, HTTPError
from unittest import TestCase, skip
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path
from shutil import copy

from launcher.mods.downloader.base import DefaultDownloader

from common import MockedResponse


data_dir: Path = Path(__file__).parent / 'data'


def mocked_get(*args, **kwargs):
    return {
        DefaultDownloaderTestCase._basic_url: MockedResponse(200, data_dir / 'test.zip'),
        DefaultDownloaderTestCase._git_url: MockedResponse(200, data_dir / 'test-git-archive.zip'),
    }.get(args[0], MockedResponse(404, None))


def mocked_retry(*args, **kwargs):
    raise ConnectionError('Mocked Error')


class DefaultDownloaderTestCase(TestCase):

    _basic_url: str = 'http://mockedURL/leet.zip'

    _git_url: str = 'https://github.com/foo/bar/archive/refs/heads/main.zip'

    def test_archive_before_download(self):
        o = DefaultDownloader(self._basic_url)

        with self.assertRaises(RuntimeError):
            o.archive

    @patch('launcher.mods.downloader.g_session.get', side_effect=mocked_get)
    def test_download_and_extract(self, mock_request):
        o = DefaultDownloader(self._basic_url)

        self.assertEqual(o.url, self._basic_url)

        with TemporaryDirectory(prefix='gamma-launcher-base-downloader-test-') as dir:
            pdir = Path(dir)

            o.download(pdir)
            self.assertEqual(o.archive, pdir / 'leet.zip')

            o.extract(pdir)
            self.assertEqual((pdir / 'flag').read_text().strip(), 'success')

        mock_request.assert_called_once_with(self._basic_url, stream=True)

    @patch('launcher.mods.downloader.g_session.get', side_effect=mocked_get)
    def test_download_with_cached(self, mock_request):
        o = DefaultDownloader(self._basic_url)

        with TemporaryDirectory(prefix='gamma-launcher-base-downloader-test-') as dir:
            pdir = Path(dir)
            archive_path = pdir / 'leet.zip'

            copy(data_dir / 'test-git-archive.zip', archive_path)

            o.download(pdir, use_cached=True)
            self.assertEqual(md5(archive_path.read_bytes()).hexdigest(), 'cf7618fe2430b2ea3652dc773288e5aa')

            o.download(pdir, use_cached=True, hash='26134043be9927512a7e47f2e4261605')
            self.assertEqual(md5(archive_path.read_bytes()).hexdigest(), '26134043be9927512a7e47f2e4261605')

        mock_request.assert_called_once_with(self._basic_url, stream=True)

    @patch('launcher.mods.downloader.g_session.get', side_effect=mocked_get)
    def test_check(self, mock_request):
        o = DefaultDownloader(self._basic_url)

        with TemporaryDirectory(prefix='gamma-launcher-base-downloader-test-') as dir:
            pdir = Path(dir)

            self.assertTrue(not o.check(pdir))

            o.download(pdir)
            self.assertTrue(o.check(pdir))

        mock_request.assert_called_once_with(self._basic_url, stream=True)

    @patch('launcher.mods.downloader.g_session.get', side_effect=mocked_get)
    def test_git_url(self, mock_request):
        o = DefaultDownloader(self._git_url)

        with TemporaryDirectory(prefix='gamma-launcher-base-downloader-test-') as dir:
            pdir = Path(dir)

            o.download(pdir)
            self.assertEqual(o.archive, pdir / 'bar-main.zip')

        mock_request.assert_called_once_with(self._git_url, stream=True)

    @patch('launcher.mods.downloader.g_session.get', side_effect=mocked_get)
    def test_not_found(self, mock_request):
        o = DefaultDownloader('http://blablabla/foobar.zip')

        with self.assertRaises(HTTPError), TemporaryDirectory(
            prefix='gamma-launcher-base-downloader-test-'
        ) as dir:
            o.download(Path(dir))

        mock_request.assert_called_once_with('http://blablabla/foobar.zip', stream=True)

    @skip('Take a minute')
    @patch('launcher.mods.downloader.g_session.get', side_effect=mocked_retry)
    def test_retry_and_fail(self, mock_request):
        o = DefaultDownloader(self._basic_url)

        with self.assertRaises(ConnectionError), TemporaryDirectory(
            prefix='gamma-launcher-base-downloader-test-'
        ) as dir:
            o.download(Path(dir))

        self.assertEqual(len(mock_request.call_args_list), 3)
