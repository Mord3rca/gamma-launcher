from git import Repo
from os import getenv, environ
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from launcher.bootstrap import is_in_pyinstaller_context
from launcher.mods.downloader.base import DefaultDownloader


if getenv("GAMMA_LAUNCHER_NO_GIT", None):
    raise NotImplementedError("NO_GIT is set, aborting PythonGit implementation")


class GithubDownloader(DefaultDownloader):

    def download(self, to: Path, use_cached: bool = False, filename: str = None) -> Path:
        if is_in_pyinstaller_context() and getenv('LD_LIBRARY_PATH'):
            del environ['LD_LIBRARY_PATH']

        user, project, *_ = self.regexp_url.match(self._url).groups()
        self._archive = to / f"{project}.git"

        if not self._archive.is_dir():
            Repo.init(self._archive, bare=True)

        repo = Repo(self._archive)
        remote = repo.create_remote(user, f"https://github.com/{user}/{project}") \
            if user not in repo.remotes else repo.remotes[user]

        print(f"    Fetching remote {user} from {self._archive.name}...")
        remote.fetch()

        return self._archive

    def extract(self, to: Path, r: str = None, tmpdir: str = None) -> None:
        user, *_, revision = self.regexp_url.match(self._url).groups()
        revision = revision if revision else f"{user}/main"
        repo = Repo(self._archive)

        with TemporaryDirectory(prefix='gamma-launcher-github-extract-') as dir:
            pdir = Path(tmpdir or dir)
            repo.git().execute(['git', 'worktree', 'add', '--detach', str(pdir), revision])
            if pdir != to:
                copytree(pdir, to, dirs_exist_ok=True)

        repo.git().execute(['git', 'worktree', 'prune'])
