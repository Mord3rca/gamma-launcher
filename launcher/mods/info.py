from typing import List, Optional


class ModInfo:

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def author(self) -> Optional[str]:
        return self._data.get('author', None)

    @property
    def name(self) -> Optional[str]:
        return self._data.get('name', None)

    @name.setter
    def name(self, name: str) -> None:
        self._data['name'] = name

    @property
    def title(self) -> Optional[str]:
        return self._data.get('title', None)

    @property
    def url(self) -> Optional[str]:
        return self._data.get('url', None)

    @property
    def iurl(self) -> Optional[str]:
        return self._data.get('iurl', None)

    @property
    def subdirs(self) -> Optional[List[str]]:
        return self._data.get('subdirs', None)
