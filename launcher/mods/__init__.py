from os.path import sep
from pathlib import Path
from typing import Dict, List

from launcher.mods.base import Base, Default
from launcher.mods.separator import Separator


__all__ = [
    'read_mod_maker'
]


def _read_mod_maker_line(line: str) -> Dict[str, str]:
    it = line.split('\t')

    return {
        'name': f'{it[3]}{it[2]}',
        'url': it[0],
        'install_directives': [
            i.replace('\\', sep).lstrip(sep) for i in it[1].split(':')
        ] if it[1] != '0' else None,
        'author': it[2].strip('- '),
        'title': it[3].strip(),
        'info_url': it[4] if len(it) >= 5 else '',
    }


def read_mod_maker(mod_list: Path, mod_make: Path) -> List[Base]:
    result = []

    print(f'[+] Reading mod definition from {mod_make.parent} ...')
    modlist = {
        i[1:].strip(): None for i in filter(
            lambda x: x.startswith('+') or x.startswith('-'),
            mod_list.read_text().split('\n')
        )
    }

    for i in filter(lambda x: x and not x.startswith(' '), mod_make.read_text().split('\n')):
        try:
            data = _read_mod_maker_line(i)
            name = data['name']
        except ValueError:
            print(f'   Skipping: {i}')

        for i in modlist.keys():
            if name in i:
                data['name'] = i
                modlist[i] = data

    for name, data in modlist.items():
        if 'separator' in name:
            result.append(Separator(name=name))
            continue

        if not data:
            continue

        result.append(Default(**data))

    return result
