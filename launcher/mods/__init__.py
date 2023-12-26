from os.path import sep
from pathlib import Path
from typing import Dict, List

from launcher.mods.base import Base, Default
from launcher.mods.large_file import GammaLargeFile
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


def read_mod_maker(mod_path: Path) -> List[Base]:
    result = []

    print(f'[+] Reading mod definition from {mod_path} ...')
    modlist = {
        i[1:].strip(): None for i in filter(
            lambda x: x.startswith('+') or x.startswith('-'),
            (mod_path / 'modlist.txt').read_text().split('\n')
        )
    }

    for i in filter(
        lambda x: x and not x.startswith(' '),
        (mod_path / 'modpack_maker_list.txt').read_text().split('\n')
    ):
        try:
            data = _read_mod_maker_line(i)
            name = data['name']
        except ValueError:
            print(f'   Skipping: {i}')

        for i in modlist.keys():
            if data['title'] in i:
                data['name'] = i
                modlist[i] = data

    for name, data in modlist.items():
        if 'separator' in name:
            result.append(Separator(name=name))
            continue

        if not data:
            continue

        if 'addons/start/222467' in data.get('url') and 'github.com' in data.get('info_url'):
            result.append(GammaLargeFile(**data))
            continue

        result.append(Default(**data))

    return result
