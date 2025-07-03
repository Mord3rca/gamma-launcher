from os.path import sep
from pathlib import Path
from typing import Dict, List, Union

from launcher.mods.archive import extract_archive
from launcher.mods.base import ModBase
from launcher.mods.installer import GitInstaller, SeparatorInstaller, DefaultInstaller
from launcher.mods.downloader import ModDBDownloader, GithubDownloader, DefaultDownloader

__all__ = [
    'read_mod_maker'
]


class ModDefault(DefaultInstaller, DefaultDownloader, ModBase):
    pass


class BaseArchive(DefaultInstaller, DefaultDownloader, ModBase):

    def __init__(self, url: str) -> None:
        super().__init__(None, url, None, None, None, None)


class ModDBArchive(ModDBDownloader, ModDefault):

    def __init__(self, name: str, url: str, iurl: str) -> None:
        super().__init__(name, url, None, None, iurl, None)

    def check(self, *args, **kwargs) -> None:
        raise NotImplementedError("Not available")

    def install(self, to: Path) -> None:
        if not self._archive:
            raise RuntimeError("Use download() method first")

        extract_archive(self._archive, to, "application/x-7z-compressed+bcj2")


class GithubArchive(GithubDownloader, ModDefault):

    def __init__(self, url: str) -> None:
        super().__init__(None, url, None, None, None, None)


class ModDBInstaller(ModDBDownloader, DefaultInstaller):
    pass


class ModSeparator(SeparatorInstaller, ModBase):
    pass


class ModGitInstaller(GithubDownloader, GitInstaller, ModDefault):
    pass


def _register_git_mod(git_mods: List[ModGitInstaller], **kwargs):
    tmp = list(filter(lambda x: x.url == kwargs.get('iurl'), git_mods))
    if tmp:
        tmp[0].append(**kwargs)
        return

    obj = ModGitInstaller(kwargs.get('iurl'))
    obj.append(**kwargs)
    git_mods += [obj]


def _parse_modpack_maker_line(line: str) -> Union[Dict[str, str], None]:
    try:
        it = line.split('\t')
        data = {
            'name': f'{it[3]}{it[2]}',
            'url': it[0],
            'add_dirs': [
                i.replace('\\', sep).lstrip(sep) for i in it[1].split(':')
            ] if it[1] != '0' else None,
            'author': it[2].strip('- '),
            'title': it[3].strip(),
            'iurl': it[4] if len(it) >= 5 else '',
        }
    except ValueError:
        print(f'   Skipping: {line}')
        return None

    return data


def read_mod_maker(mod_path: Path) -> List[ModBase]:  # noqa: C901
    result = []
    git_mods = []

    print(f'[+] Reading mod definition from {mod_path} ...')
    modlist = {
        i[1:].strip(): None for i in filter(
            lambda x: x.startswith('+') or x.startswith('-'),
            (mod_path / 'modlist.txt').read_text().split('\n')
        )
    }
    modmaker = [
        _parse_modpack_maker_line(i) for i in filter(
            lambda x: x and not x.startswith(' '),
            (mod_path / 'modpack_maker_list.txt').read_text().split('\n')
        )
    ]
    modmaker = list(filter(lambda x: x is not None, modmaker))

    # Strict search (match title - author)
    for i in modlist.keys():
        for m in modmaker.copy():
            if m['name'] in i:
                m['name'] = i
                modlist[i] = m
                modmaker.remove(m)
                break

    # Not so strict search (match only title)
    for i in modlist.keys():
        for m in modmaker.copy():
            if m['title'] in i:
                m['name'] = i
                modlist[i] = m
                modmaker.remove(m)
                break

    for m in modmaker:
        print(f'WARN: No mod folder found for {m["name"]}')

    for name, data in modlist.items():
        if 'separator' in name:
            result.append(ModSeparator(name))
            continue

        if not data:
            continue

        if 'addons/start/222467' in data.get('url') and 'github.com' in data.get('iurl'):
            _register_git_mod(git_mods, **data)
            continue

        if 'moddb.com' in data.get('url'):
            result.append(ModDBInstaller(**data))
            continue

        result.append(ModDefault(**data))

    # Not in the list but installed by Official Launcher. Not gonna ask why.
    _register_git_mod(git_mods, **{
        'name': 'Burn\'s Optimised World Models',
        'url': 'https://www.moddb.com/addons/start/222467',
        'add_dirs': None,
        'author': 'Burn',
        'title': 'Burn\'s Optimised World Models',
        'iurl': 'https://github.com/Grokitach/gamma_large_files_v2',
    })

    # In the list but don't have iurl so this is ignored.
    _register_git_mod(git_mods, **{
        'name': 'Retrogue\'s Additional Weapons',
        'url': 'https://www.moddb.com/addons/start/222467',
        'add_dirs': None,
        'author': 'Retrogue',
        'title': 'Retrogue\'s Additional Weapons',
        'iurl': 'https://github.com/Grokitach/gamma_large_files_v2',
    })

    _register_git_mod(git_mods, **{
        'name': '405- IWP Benelli - frostychun',
        'url': 'https://www.moddb.com/addons/start/222467',
        'add_dirs': None,
        'author': 'frostychun',
        'title': 'IWP Benelli',
        'iurl': 'https://github.com/Grokitach/gamma_large_files_v2',
    })
    _register_git_mod(git_mods, **{
        'name': '407- IWP MP9 - frostychun',
        'url': 'https://www.moddb.com/addons/start/222467',
        'add_dirs': None,
        'author': 'frostychun',
        'title': 'IWP MP9',
        'iurl': 'https://github.com/Grokitach/gamma_large_files_v2',
    })

    return git_mods + result
