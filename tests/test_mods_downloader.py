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

    def test_github_downloader_receives_branch(self):
        """Verify branch is forwarded from ModInfo to GithubDownloader."""
        info = ModInfo({'url': 'https://github.com/Mord3rca/gamma-launcher', 'branch': 'dev2'})

        # We can't fully instantiate the real downloader without network/git,
        # so we verify the factory passes the branch argument correctly.
        # Instead, test that DownloaderFactory calls GithubDownloader with the branch kwarg.
        # We do this by patching the GithubDownloader constructor.
        import launcher.mods.downloader as mod
        from unittest.mock import patch

        with patch.object(mod, 'GithubDownloader', wraps=mod.GithubDownloader) as mock_dl:
            mod.DownloaderFactory(info)
            mock_dl.assert_called_once_with(info.url, branch='dev2')


class GithubDownloaderGitBranchTestCase(TestCase):
    """Tests for branch support in git.py GithubDownloader."""

    def test_defaults_to_main_when_branch_none(self):
        from launcher.mods.downloader.github.git import GithubDownloader as GitDL
        dl = GitDL("https://github.com/foo/bar")
        self.assertIsNone(dl._branch)

    def test_stores_branch_when_provided(self):
        from launcher.mods.downloader.github.git import GithubDownloader as GitDL
        dl = GitDL("https://github.com/foo/bar", branch="dev2")
        self.assertEqual(dl._branch, "dev2")

    def test_set_vars_uses_branch(self):
        """Verify _set_vars resolves to the correct branch reference."""
        from launcher.mods.downloader.github.git import GithubDownloader as GitDL
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            to = Path(tmp)
            dl = GitDL("https://github.com/foo/bar", branch="dev2")
            dl._set_vars(to)
            self.assertEqual(dl._revision, "foo/dev2")

    def test_set_vars_defaults_main(self):
        from launcher.mods.downloader.github.git import GithubDownloader as GitDL
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            to = Path(tmp)
            dl = GitDL("https://github.com/foo/bar")
            dl._set_vars(to)
            self.assertEqual(dl._revision, "foo/main")


class GithubDownloaderLegacyBranchTestCase(TestCase):
    """Tests for branch support in legacy.py GithubDownloader."""

    def test_stores_branch_when_provided(self):
        from launcher.mods.downloader.github.legacy import GithubDownloader as LegacyDL
        dl = LegacyDL("https://github.com/foo/bar", branch="dev2")
        self.assertEqual(dl._branch, "dev2")

    def test_defaults_to_none_when_not_provided(self):
        from launcher.mods.downloader.github.legacy import GithubDownloader as LegacyDL
        dl = LegacyDL("https://github.com/foo/bar")
        self.assertIsNone(dl._branch)
