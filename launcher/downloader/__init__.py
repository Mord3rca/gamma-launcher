from .github import Github
from .moddb import ModDB
from .base import Base

from urllib.parse import urlparse


def get_handler_for_url(url: str) -> Base:
    host = urlparse(url).hostname
    return {
        'github.com': Github,
        'www.moddb.com': ModDB,
    }.get(host)(url)
