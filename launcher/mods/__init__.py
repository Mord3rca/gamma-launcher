from itertools import chain
from os.path import sep
from pathlib import Path
from typing import Dict, List, Optional

from launcher.mods.info import ModInfo
from launcher.mods.installer import BaseInstaller, DefaultInstaller, GitResourceInstaller, SeparatorInstaller

__all__ = [
    'read_mod_maker'
]


class ModDefault(DefaultInstaller):
    pass


class BaseArchive(BaseInstaller):

    def __init__(self, url: str) -> None:
        super().__init__(ModInfo({"url": url}))


GithubArchive = BaseArchive  # For compat: DownloaderFactory will instanciate correct handler


class ModDBArchive(BaseInstaller):

    def __init__(self, name: str, url: str, iurl: str) -> None:
        super().__init__(ModInfo({"name": name, "url": url, "iurl": iurl}))


class ModDBInstaller(DefaultInstaller):
    pass


class ModSeparator(SeparatorInstaller):

    def download(self, *args, **kwargs) -> Path:
        return Path()  # Separator doesn't actually download anything

    def extract(self, *args, **kwargs) -> None:
        pass


class GitResource(GitResourceInstaller):

    def __init__(self, url: str, gamedata: bool = False) -> None:
        super().__init__(ModInfo({'url': url}), gamedata)


def _parse_modpack_maker_line(line: str) -> ModInfo:
    it = line.split('\t')
    args = tuple(
        chain.from_iterable([i.split(' ') for i in it[5:]])
    ) if len(it) > 5 else None
    data = {
        'name': f'{it[3]}{it[2]}',
        'url': it[0],
        'subdirs': [
            i.replace('\\', sep).lstrip(sep) for i in it[1].split(':')
        ] if it[1] != '0' else None,
        'author': it[2].strip('- '),
        'title': it[3].strip(),
        'iurl': it[4] if len(it) >= 5 else '',
        'args': args,
    }
    return ModInfo(data)


def read_mod_maker(mod_path: Path) -> List[ModSeparator | ModDBInstaller | ModDefault]:  # noqa: C901
    result = []

    print(f'[+] Reading mod definition from {mod_path} ...')
    modlist: Dict[str, Optional[ModInfo]] = {
        i[1:].strip(): None for i in filter(
            lambda x: x.startswith('+') or x.startswith('-'),
            (mod_path / 'modlist.txt').read_text().split('\n')
        )
    }
    # Parse modpack_maker_list.txt lines into ModInfo objects
    # Skip lines that are empty, start with spaces, or fail to parse
    modmaker: List[ModInfo] = []
    for i in filter(
        lambda x: x and not x.startswith(' '),
        (mod_path / 'modpack_maker_list.txt').read_text().split('\n')
    ):
        try:
            modmaker.append(_parse_modpack_maker_line(i))
        except (ValueError, IndexError):
            print(f'   Skipping: {i}')

    # Strict search (match title - author)
    for i in modlist.keys():
        for m in modmaker.copy():
            if m.name in i:
                m.name = i
                modlist[i] = m
                modmaker.remove(m)
                break

    # Not so strict search (match only title)
    for i in modlist.keys():
        for m in modmaker.copy():
            if m.title in i:
                m.name = i
                modlist[i] = m
                modmaker.remove(m)
                break

    for m in modmaker:
        print(f'WARN: No mod folder found for {m.name}')

    for name, data in modlist.items():
        if 'separator' in name:
            result.append(ModSeparator(name))
            continue

        if not data:
            continue

        # Placeholder for Git provided mods
        if 'addons/start/222467' in data.url and 'github.com' in data.iurl:
            continue

        if 'moddb.com' in data.url:
            result.append(ModDBInstaller(data))
            continue

        result.append(ModDefault(data))

    return result
