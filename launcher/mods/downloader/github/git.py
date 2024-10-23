from git import Repo
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from launcher.mods.downloader.base import DefaultDownloader


class GithubDownloader(DefaultDownloader):

    def download(self, to: Path, use_cached: bool = False, filename: str = None) -> Path:
        user, project = self.regexp_url.match(self._url).groups()
        self._archive = to / f"{project}.git"

        if not self._archive.is_dir():
            Repo.init(self._archive, bare=True)

        repo = Repo(self._archive)
        remote = repo.create_remote(user, self._url) if user not in repo.remotes else repo.remotes[user]

        print(f"    Fetching remote {user} from {self._archive.name}...")
        remote.fetch()

        return self._archive

    def extract(self, to: Path, r: str = None, tmpdir: str = None) -> None:
        user, _ = self.regexp_url.match(self._url).groups()
        repo = Repo(self._archive)

        with TemporaryDirectory(prefix='gamma-launcher-github-extract-') as dir:
            pdir = Path(tmpdir or dir)
            repo.git().execute(['git', 'worktree', 'add', '--detach', str(pdir), f'{user}/main'])
            if pdir != to:
                copytree(pdir, to, dirs_exist_ok=True)

        repo.git().execute(['git', 'worktree', 'prune'])
