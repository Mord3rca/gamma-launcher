from pathlib import Path
from re import compile

from .base import Base, g_session


class Github(Base):

    regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)/?")

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._filename = super().filename

        self._decode_url()

    def _decode_url(self) -> None:
        user, project = self.regexp_url.match(self._url).groups()

        if "release" in self._url or self._url.endswith(".zip"):
            revision = Path(self._url).name.split('.')[0]
            self._filename = f"{project}-{revision}.zip"
            return

        branch = g_session.get(
            f"https://api.github.com/repos/{user}/{project}",
            headers={"Accept": "application/json"}
        ).json()["default_branch"]
        self._url = f"https://github.com/{user}/{project}/archive/refs/heads/{branch}.zip"
        self._filename = f"{project}-{branch}.zip"

    @property
    def filename(self) -> str:
        return self._filename
