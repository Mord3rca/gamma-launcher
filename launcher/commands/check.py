import os
from bs4 import BeautifulSoup
from hashlib import file_digest
from pathlib import Path
from typing import Dict

from launcher.downloader.base import g_session
from launcher.downloader import get_handler_for_url
from launcher.commands.common import read_mod_maker
from launcher.commands.install import FullInstall


def parse_moddb_data(url: str) -> Dict[str, str]:
    soup = BeautifulSoup(g_session.get(url).text, features="html.parser")
    result = {}

    for i in soup.body.find_all('div', attrs={'class': "row clear"}):
        try:
            name = i.h5.text
            value = i.span.text.strip()
        except AttributeError:
            # if div have no h5 or span child, just ignore it.
            continue

        # We can parse more, but we don't need it.
        if name in ('Filename', 'MD5 Hash'):
            result[name] = value

    return result


class CheckMD5:

    arguments: dict = {
        "--gamma": {
            "help": "Path to GAMMA directory",
            "required": True,
            "type": str
        },
        "--redownload": {
            "help": "Redownloads a mod if the MD5 sums do not match",
            "required": False,
            "action": "store_true"
        },
    }

    name: str = "check-md5"

    help: str = "Check MD5 hash for all addons"

    def run(self, args) -> None:
        errors = []
        modpack_dl_dir = Path(args.gamma) / "downloads"
        modpack_data_dir = Path(args.gamma) / ".Grok's Modpack Installer" / "G.A.M.M.A" / "modpack_data"
        redownload = args.redownload

        mod_maker = read_mod_maker(
            modpack_data_dir / 'modlist.txt',
            modpack_data_dir / 'modpack_maker_list.txt'
        )

        print('-- Starting MD5 Check')
        for i in filter(lambda x: x[1] and x[1]["info_url"], mod_maker.items()):
            k, v = i[0], i[1]

            try:
                info = parse_moddb_data(v['info_url'])
                file = modpack_dl_dir / info['Filename']
            except KeyError:
                print(f"  !! Can't parse moddb page for {v['info_url']}")
                errors += [f"Error: parsing failure for {v['info_url']}"]
                continue

            if not file.exists():
                errors += [f"Error: {file.name} not found on disk"]
                print(f"{file.name} do not exist, skiping")
                continue

            with open(file, 'rb') as f:
                md5 = file_digest(f, 'md5').hexdigest()
            print(f"{file.name} remote hash is: '{info['MD5 Hash']}'")
            print(f"{file.name} local  hash is: '{md5}'")

            if md5 != info['MD5 Hash']:
                errors += [f"Error: {file.name} -- remote({info['MD5 Hash']}) != local({md5})"]
                if redownload:
                    print(f"Redownloading {file.name}...")
                    if self.redownload(k, v, args.gamma):
                        print(f"{file.name} downloaded successfully")
                    else:
                        error = f"Error: {file.name} failed MD5 check after being redownloaded"
                        print(error)
                        errors += [error]
                else:
                    print('  !! Please update your installation')

            print('-' * 25)

        for err in errors:
            print(err)

    def redownload(self, name, dict, gamma_dir):
        full_install = FullInstall()
        full_install._dl_dir = os.path.join(gamma_dir, "downloads")
        full_install._mod_dir = os.path.join(gamma_dir, "mods")
        full_install._install_mod(name, dict, use_cached=False)

        # Check MD5 sum again
        e = get_handler_for_url(dict["url"])
        file = os.path.join(full_install._dl_dir, e.filename)
        info = parse_moddb_data(dict["info_url"])

        with open(file, 'rb') as f:
            local_md5 = file_digest(f, 'md5').hexdigest()
        print(f"{info['Filename']} remote hash is: '{info['MD5 Hash']}'")
        print(f"{info['Filename']} local  hash is: '{local_md5}'")

        return info["MD5 Hash"] == local_md5
