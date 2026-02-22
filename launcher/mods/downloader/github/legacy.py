from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Optional

from launcher.archive import extract_archive
from launcher.mods.info import ModInfo
from launcher.mods.downloader.base import DefaultDownloader, g_session


class GithubDownloader(DefaultDownloader):

    def __init__(self, info: ModInfo) -> None:
        super().__init__(info.url, *(info.args or ()))
        self._revision = None

    def download(self, to: Path, use_cached: bool = False, filename: str = "") -> Path:  # type: ignore[override]
        # Note: Using 'filename' instead of 'hash' - legacy downloader allows custom archive names
        # Signature doesn't match base class but preserves original functionality
        match = self.regexp_url.match(self._url)
        if not match:
            raise ValueError(f"Invalid GitHub URL: {self._url}")

        user, project, *_ = match.groups()

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
            extract_archive(str(self.archive), str(pdir))

            # Detect if the archive contains a dir containing the git tree
            ldir = list(pdir.iterdir())
            if len(ldir) == 1:
                pdir = ldir[0]

            copytree(pdir, to, dirs_exist_ok=True)

    @property
    def revision(self) -> Optional[str]:
        return self._revision
