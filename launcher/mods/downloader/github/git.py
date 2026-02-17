from git import Repo, RemoteProgress
from os import getenv, environ
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from tqdm import tqdm
from typing import Optional

from launcher.bootstrap import is_in_pyinstaller_context
from launcher.mods.info import ModInfo
from launcher.mods.downloader.base import DefaultDownloader

if getenv("GAMMA_LAUNCHER_NO_GIT", None):
    raise NotImplementedError("NO_GIT is set, aborting PythonGit implementation")


class ProgressPrinter(RemoteProgress):
    """
    A portable, clean, and clear progress printer for GitPython fetch operations.
    Prints progress on a single line with elapsed time in [HH:MM:SS] format.
    Uses only standard Python and ANSI codes for best portability.
    """
    def __init__(self, name: str, user: str):
        super().__init__()
        self._pbar = tqdm(
            desc=f"  - Fetching remote {user} from {name}",
            unit="object", unit_scale=True
        )

    def update(self, op_code, cur_count, max_count=None, message=''):
        if not message:
            return
        self._pbar.total = max_count
        self._pbar.n = cur_count
        self._pbar.refresh()


class GithubDownloader(DefaultDownloader):

    def __init__(self, info: ModInfo) -> None:
        super().__init__(info)
        self._revision = None

    def download(self, to: Path, use_cached: bool = False, filename: str = None) -> Path:
        if is_in_pyinstaller_context() and getenv('LD_LIBRARY_PATH'):
            del environ['LD_LIBRARY_PATH']

        user, project, *_, revision = self.regexp_url.match(self._url).groups()
        self._archive = to / f"{project}.git"
        self._revision = revision if revision else f"{user}/main"

        if not self._archive.is_dir():
            Repo.init(self._archive, bare=True)

        repo = Repo(self._archive)
        remote = repo.create_remote(user, f"https://github.com/{user}/{project}") \
            if user not in repo.remotes else repo.remotes[user]

        remote.fetch(progress=ProgressPrinter(self._archive.name, user))

        return self._archive

    def extract(self, to: Path) -> None:
        repo = Repo(self._archive)

        with TemporaryDirectory(prefix='gamma-launcher-github-extract-') as dir:
            pdir = Path(dir)
            repo.git().execute(['git', 'worktree', 'add', '--detach', str(pdir), self._revision])
            if pdir != to:
                copytree(pdir, to, dirs_exist_ok=True)

        repo.git().execute(['git', 'worktree', 'prune'])

    @property
    def revision(self) -> Optional[str]:
        return Repo(self._archive).rev_parse(self._revision).hexsha if self._revision else None
