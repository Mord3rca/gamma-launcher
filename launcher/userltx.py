from pathlib import Path


class UserLTX:
    'Object used to create / edit user.ltx file'

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
                self.__content[f'{key} {args[0]}'] = ' '.join(args[1:])
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
            data += f'{key} {value}\r\n' if value else f'{key}\r\n'

        file.write_text(data)
