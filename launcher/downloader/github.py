from re import compile

from .base import Base, g_session


class Github(Base):

    regexp_url = compile("https?://github.com/(\w+)/(\w+)/?")

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._project = None

        self._decode_url(url)

    def _decode_url(self, url: str) -> None:
        user, self._project = self.regexp_url.match(url).groups()

        if(not url.endswith(".zip")):
            branch = g_session.get(
                f"https://api.github.com/repos/{user}/{self._project}",
                headers={"Accept": "application/json"}
            ).json()["default_branch"]
            self._url = f"https://github.com/{user}/{self._project}/archive/refs/heads/{branch}.zip"

    @property
    def filename(self) -> str:
        return f"{self._project}.zip"
