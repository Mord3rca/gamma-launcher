from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Optional

from launcher.archive import extract_archive
from launcher.mods.info import ModInfo
from launcher.mods.downloader.base import DefaultDownloader, g_session


class GithubDownloader(DefaultDownloader):
    """Specialization of `launcher.mods.downloader.base.DefaultDownloader`
    to manage Github URLs without `GitPython` module
    """

    def __init__(self, info: ModInfo) -> None:
        super().__init__(info)
        self._revision = None

    def check(self, to: Path, update_cache: bool = False) -> None:
        pass

    def download(self, to: Path, use_cached: bool = False, filename: str = None) -> Path:
        user, project, *_ = self.regexp_url.match(self._url).groups()

        if "release" in self._url or self._url.endswith(".zip"):
            self._revision = Path(self._url).name.split('.')[0]
            self._archive = to / (filename or f"{project}-{self._revision}.zip")
            return super().download(to, use_cached)

        branch = g_session.get(
            f"https://api.github.com/repos/{user}/{project}",
            headers={"Accept": "application/json"}
        ).json()["default_branch"]

        self._revision = g_session.get(
            f"https://api.github.com/repos/{user}/{project}/branches/{branch}",
            headers={"Accept": "application/json"}
        ).json()["commit"]["sha"]

        self._url = f"https://github.com/{user}/{project}/archive/refs/heads/{branch}.zip"
        self._archive = to / (filename or f"{project}-{self._revision}.zip")

        return super().download(to, use_cached)

    def extract(self, to: Path) -> None:
        with TemporaryDirectory(prefix='gamma-launcher-github-extract-') as dir:
            pdir = Path(dir)
            extract_archive(self.archive, str(pdir))

            # Detect if the archive contains a dir containing the git tree
            ldir = list(pdir.iterdir())
            if len(ldir) == 1:
                pdir = ldir[0]

            copytree(pdir, to, dirs_exist_ok=True)

    @property
    def revision(self) -> Optional[str]:
        return self._revision
