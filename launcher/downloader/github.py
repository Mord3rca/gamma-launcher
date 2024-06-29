from git import Repo, RemoteProgress
from os import getenv
from pathlib import Path
from re import compile
from subprocess import run, DEVNULL
from tqdm import tqdm
from typing import Dict, Union

from .base import Base, g_session

# See if we can use git to speedup updates etc
_with_git = True
try:
    run(['git', '--version'], stdout=DEVNULL, stderr=DEVNULL)
except FileNotFoundError:
    print("[*] git not found on your system or not in PATH, using DL method for git repos")
    _with_git = False

_git_regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)/?")


class _TqdmProgress(RemoteProgress):

    def __init__(self) -> None:
        super().__init__()

        self._tqdm = tqdm(desc="Fetching origin: ", unit=" object(s)")

    def update(self, op_code, cur_count, max_count=None, msg=None) -> None:
        self._tqdm.update(cur_count)


class _WithGitPy(Base):

    def __init__(self, url: str, info: Dict) -> None:
        super().__init__(url)
        self._filename = f"{info['project']}.git"

    @property
    def filename(self) -> str:
        return self._filename

    def md5(self) -> str:
        raise NotImplementedError("Not supported by git repos with GitPython")

    def download(self, path: str) -> None:
        p = Path(path)

        if not p.is_dir():
            Repo.clone_from(self._url, p, _TqdmProgress(), mirror=True)
            return

        # Fetching origin
        Repo(p).remotes[0].fetch(None, _TqdmProgress())


class _WithoutGitPy(Base):

    regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)/?")

    def __init__(self, url: str, info: Dict) -> None:
        super().__init__(url)

        self._filename = f"{info['project']}-{info['default_branch']}.zip" \
            if info['is_repo_url'] else f"{info['project']}-{info['revision']}.zip"

    @property
    def filename(self) -> str:
        return self._filename


def _git_project_info(url: str) -> Dict:
    info = {'is_repo_url': True}
    user, project = _git_regexp_url.match(url).groups()

    info['user'] = user
    info['project'] = project

    if "release" in url or url.endswith(".zip"):
        info['revision'] = Path(url).name.split('.')[0]
        info['is_repo_url'] = False
        return info

    info['default_branch'] = g_session.get(
        f"https://api.github.com/repos/{user}/{project}",
        headers={"Accept": "application/json"}
    ).json()["default_branch"]

    return info


# Return correct object based on config detection
def _git_bootstrap(url: str) -> Union[_WithGitPy, _WithoutGitPy]:

    info = _git_project_info(url)

    if not info['is_repo_url'] or not _with_git or getenv('GAMMA_LAUNCHER_NO_GIT', None) is not None:
        return _WithoutGitPy(url, info)

    return _WithGitPy(url, info)


Github = _git_bootstrap
