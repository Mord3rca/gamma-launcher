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
