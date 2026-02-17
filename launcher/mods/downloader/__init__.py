from typing import Optional

from launcher.mods.info import ModInfo

from .base import DefaultDownloader, g_session
from .moddb import ModDBDownloader

try:
    from .github.git import GithubDownloader
except Exception:
    print('[!] Cannot use GIT, make sure it is in your PATH. Using legacy method')
    from .github.legacy import GithubDownloader


__all__ = [
    'DefaultDownloader', 'GithubDownloader', 'g_session', 'ModDBDownloader'
]


def DownloaderFactory(info: ModInfo) -> Optional[DefaultDownloader]:
    if not info.url:
        return None

    if 'moddb.com' in info.url:
        return ModDBDownloader(info.url, info.iurl)

    if 'github.com' in info.url and not info.url.endswith(('.zip', '.7z', '.rar')):
        return GithubDownloader(info.url)

    return DefaultDownloader(info.url)
