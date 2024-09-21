from pathlib import Path
from re import compile
from shutil import copytree, move
from tempfile import TemporaryDirectory

from launcher.mods.archive import extract_archive
from launcher.mods.downloader.base import DefaultDownloader, g_session


class GithubDownloader(DefaultDownloader):

    regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)/?")

    def download(self, to: Path, use_cached: bool = False, filename: str = None) -> Path:
        user, project = self.regexp_url.match(self._url).groups()

        if "release" in self._url or self._url.endswith(".zip"):
            revision = Path(self._url).name.split('.')[0]
            self._archive = to / (filename or f"{project}-{revision}.zip")
            return

        branch = g_session.get(
            f"https://api.github.com/repos/{user}/{project}",
            headers={"Accept": "application/json"}
        ).json()["default_branch"]
        self._url = f"https://github.com/{user}/{project}/archive/refs/heads/{branch}.zip"
        self._archive = to / (filename or f"{project}-{branch}.zip")

        return super().download(to, use_cached)

    def extract(self, to: Path, r: str = None, tmpdir: str = None) -> None:
        with TemporaryDirectory(prefix='gamma-launcher-github-extract-') as dir:
            pdir = Path(tmpdir or dir)
            extract_archive(self.archive, str(pdir))

            if r:
                d = list(pdir.glob(r))[0]
                for i in d.glob("*"):
                    move(i, pdir)
                d.rmdir()

            if pdir == to:
                return

            copytree(pdir, to, dirs_exist_ok=True)
