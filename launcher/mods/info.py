from typing import List, Optional


class ModInfo:

    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def author(self) -> str:
        return self._data.get('author', '')

    @property
    def name(self) -> str:
        return self._data.get('name', '')

    @name.setter
    def name(self, name: str) -> None:
        self._data['name'] = name

    @property
    def title(self) -> str:
        return self._data.get('title', '')

    @property
    def url(self) -> str:
        return self._data.get('url', '')

    @property
    def iurl(self) -> str:
        return self._data.get('iurl', '')

    @property
    def subdirs(self) -> Optional[List[str]]:
        return self._data.get('subdirs', None)
