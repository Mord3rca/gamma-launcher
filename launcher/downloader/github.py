from .base import Base


class Github(Base):

    @property
    def filename(self) -> str:
        e = list(filter(None, self._url.split('/')))
        filename = e[e.index('github.com') + 2]
        return f"{filename}.zip"
