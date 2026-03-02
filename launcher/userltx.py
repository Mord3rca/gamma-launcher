from __future__ import annotations

from pathlib import Path


class UserLTX:
    'Object used to create / edit user.ltx file'

    class Bind(dict):

        _azerty_map: dict = {
            'kW': 'kZ', 'kA': 'kQ', 'kQ': 'kA', 'kW': 'kZ', 'kM': 'kCOMMA'
        }

        _dvorak_map: dict = {
            'kW': 'kCOMMA', 'kS': 'kO', 'kD': 'kE', 'kQ': 'kAPOSTROPHE',
            'kE': 'kPERIOD', 'kU': 'kF', 'kF': 'kU', 'kR': 'kP'
        }

        def __init__(self, type: str) -> None:
            super().__init__()
            self.__type = type

        def __str__(self) -> str:
            return '\r\n'.join([f'{self.__type} {k} {v}' for k, v in self.items()])

        def to_azerty_layout(self) -> None:
            'Change bind from QWERTY to AZERTY layout'
            for k, v in self.items():
                if v not in self._azerty_map.keys():
                    continue
                self[k] = self._azerty_map[v]

        def to_dvorak_layout(self) -> None:
            'Change bind from QWERTY to DVORAK layout'
            for k, v in self.items():
                if v not in self._dvorak_map.keys():
                    continue
                self[k] = self._dvorak_map[v]

    def __init__(self, file: Path | str = None) -> None:
        self.__content = dict()
        self.__file = None

        if file:
            self.load(file)

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        self.save(self.__file)

    def __getitem__(self, key: str) -> str:
        return self.__content[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.__content[key] = value

    @property
    def bind(self) -> UserLTX.Bind:
        'Return and instance of `UserLTX.Bind` which manage primary binds'
        if 'bind' not in self.__content:
            self.__content['bind'] = self.Bind('bind')
        return self.__content['bind']

    @property
    def bind_sec(self) -> UserLTX.Bind:
        'Return and instance of `UserLTX.Bind` which manage secondary binds'
        if 'bind_sec' not in self.__content:
            self.__content['bind_sec'] = self.Bind('bind_sec')
        return self.__content['bind_sec']

    def load(self, file: Path | str) -> None:
        '''Read ltx file

        Argument(s):
        * file -- File path (or str) to load from
        '''
        file = Path(file) if file else self.__file

        for line in file.read_text().split('\n'):
            if not line:
                continue

            key, *args = line.strip().split(' ')
            if 'bind' in key:
                if key not in self.__content:
                    self.__content[key] = self.Bind(key)
                self.__content[key][args[0]] = ' '.join(args[1:])
            else:
                self.__content[key] = ' '.join(args)

        self.__file = file

    def save(self, file: Path | str = None) -> None:
        '''Save ltx file

        Argument(s):
        * file -- File path (or str) to save to
        '''
        file = Path(file) if file else self.__file
        data = ''

        if not file:
            raise ValueError('file output need to defined in constructor or as argument of save()')

        for key, value in self.__content.items():
            if isinstance(value, self.Bind):
                data += f'{value}\r\n'
            elif not value:
                data += f'{key}\r\n'
            else:
                data += f'{key} {value}\r\n'

        file.write_text(data)
