from git import Repo, RemoteProgress
from os import getenv, environ
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Optional
import time

from launcher.bootstrap import is_in_pyinstaller_context
from launcher.mods.downloader.base import DefaultDownloader

if getenv("GAMMA_LAUNCHER_NO_GIT", None):
    raise NotImplementedError("NO_GIT is set, aborting PythonGit implementation")


class ProgressPrinter(RemoteProgress):
    """
    A portable, clean, and clear progress printer for GitPython fetch operations.
    Prints progress on a single line with elapsed time in [HH:MM:SS] format.
    Uses only standard Python and ANSI codes for best portability.
    """
    def __init__(self):
        super().__init__()
        self._start_time = time.monotonic()

    def update(self, op_code, cur_count, max_count=None, message=''):
        if not message:
            return
        elapsed = int(time.monotonic() - self._start_time)
        hms = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        line = f"[git fetch] {message} | [{hms}]"
        clear = '\033[K' if self._is_ansi() else ''
        # Pad to 80 chars for clean overwrite
        print(f"\r{clear}{line:<80}", end='', flush=True)

    def _is_ansi(self):
        # Basic check for ANSI support (most modern terminals)
        import sys
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def __del__(self):
        print()  # Ensure the next print starts on a new line


class GithubDownloader(DefaultDownloader):

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

        print(f"    Fetching remote {user} from {self._archive.name}...")
        remote.fetch(progress=ProgressPrinter())
        print()  # Ensure the next print starts on a new line after fetch

        return self._archive

    def extract(self, to: Path, r: str = None, tmpdir: str = None) -> None:
        repo = Repo(self._archive)

        with TemporaryDirectory(prefix='gamma-launcher-github-extract-') as dir:
            pdir = Path(tmpdir or dir)
            repo.git().execute(['git', 'worktree', 'add', '--detach', str(pdir), self._revision])
            if pdir != to:
                copytree(pdir, to, dirs_exist_ok=True)

        repo.git().execute(['git', 'worktree', 'prune'])

    def revision(self) -> Optional[str]:
        return Repo(self._archive).rev_parse(self._revision).hexsha if self._revision else None
