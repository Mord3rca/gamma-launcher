from re import compile

from .base import Base, g_session


class Github(Base):

    regexp_url = compile("https?://github.com/([\\w_.-]+)/([\\w_.-]+)/?")

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._filename = super().filename

        self._decode_url()

    def _decode_url(self) -> None:
        if "release" in self._url or self._url.endswith(".zip"):
            return

        user, project = self.regexp_url.match(self._url).groups()
        branch = g_session.get(
            f"https://api.github.com/repos/{user}/{project}",
            headers={"Accept": "application/json"}
        ).json()["default_branch"]
        self._url = f"https://github.com/{user}/{project}/archive/refs/heads/{branch}.zip"
        self._filename = f"{project}.zip"

    @property
    def filename(self) -> str:
        return self._filename
