import os
from typing import Dict


def _read_mod_list(mod_list) -> Dict[str, None]:
    with open(mod_list) as f:
        d = f.read()
    return {
        i[1:].strip(): None for i in filter(lambda x: x.startswith('+') or x.startswith('-'), d.split('\n'))
    }


def read_mod_maker(mod_list, mod_make) -> Dict[str, Dict]:
    print(f'[+] Reading {mod_list} & {mod_make}...')
    mods_make = _read_mod_list(mod_list)
    with open(mod_make, 'r') as f:
        d = f.read()
    for i in filter(lambda x: x and not x.startswith(' '), d.split('\n')):
        try:
            mod = None
            it = i.split('\t')
            for i in mods_make.keys():
                if f"{it[3]}{it[2]}" in i:
                    mod = i
                    break
            else:
                continue

            mods_make[mod] = {
                'url': it[0],
                'install_directives': [
                     i.replace('\\', os.path.sep).lstrip(os.path.sep) for i in it[1].split(':')
                 ] if it[1] != '0' else None,
                'author': it[2],
                'title': it[3],
                'info_url': it[4] if len(it) >= 5 else '',
            }
        except ValueError:
            print(f'   Skipping: {i}')

    return mods_make
