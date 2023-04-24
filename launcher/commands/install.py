import os

from distutils.dir_util import copy_tree, DistutilsFileError
from shutil import copy2, move
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional

from launcher.archive import extract_archive
from launcher.downloader import get_handler_for_url
from launcher.meta import create_ini_file, create_ini_separator_file


class FullInstall:

    arguments: dict = {
        "--anomaly": {
            "help": "Path to ANOMALY directory",
            "required": True,
            "type": str
        },
        "--gamma": {
            "help": "Path to GAMMA directory",
            "required": True,
            "type": str
        },
    }

    name: str = "full_install"

    help: str = "Complete install of S.T.A.L.K.E.R.: G.A.M.M.A."

    def __init__(self):
        self._anomaly_dir = None
        self._gamma_dir = None

        self._dl_dir = None
        self._mod_dir = None
        self._grok_mod_dir = None

        self._mods = []
        self._mods_make = {}

    def _update_gamma_definition(self) -> None:
        print('[+] Updating G.A.M.M.A. definition')
        gdef = f'{self._grok_mod_dir}/GAMMA_definition.zip'

        if not os.path.isfile(gdef):
            print('    downloading archive...')
            g = get_handler_for_url("https://github.com/Grokitach/Stalker_GAMMA/archive/refs/heads/main.zip")
            g.download(gdef)

        with TemporaryDirectory(prefix="gamma-launcher-") as dir:
            extract_archive(gdef, dir)
            copy_tree(f"{dir}/Stalker_GAMMA-main", self._grok_mod_dir)

        move(
            os.path.join(self._grok_mod_dir, 'G.A.M.M.A_definition_version.txt'),
            os.path.join(self._grok_mod_dir, 'version.txt')
        )

    def _patch_anomaly(self) -> None:
        copy_tree(
            os.path.join(self._grok_mod_dir, 'G.A.M.M.A', 'modpack_patches'),
            self._anomaly_dir
        )

    def _read_mod_list(self) -> List[str]:
        path = os.path.join(self._grok_mod_dir, 'G.A.M.M.A', 'modpack_data', 'modlist.txt')
        print(f'[+] Reading modlist {path}...')
        with open(path) as f:
            d = f.read()
        return [
            i[1:].strip() for i in filter(lambda x: x.startswith('+') or x.startswith('-'), d.split('\n'))
        ]

    def _read_mod_maker(self) -> Dict[str, Dict]:
        path = os.path.join(self._grok_mod_dir, 'G.A.M.M.A', 'modpack_data', 'modpack_maker_list.txt')
        print(f'[+] Reading modpack maker ({path})...')
        mods_make = {}
        with open(path, 'r') as f:
            d = f.read()
        for i in filter(lambda x: x and not x.startswith(' '), d.split('\n')):
            try:
                it = i.split('\t')
                mods_make[f"{it[3]}{it[2]}"] = {
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

    def _find_mod_make_directive(self, title) -> Optional[Dict]:
        for k, v in self._mods_make.items():
            if k in title:
                return v

        return None

    def _install_mod(self, name: str) -> None:
        install_dir = os.path.join(self._mod_dir, name)

        # Special case, it's a separator
        if 'separator' in name:
            print(f'[+] Installing separator: {name}')
            os.makedirs(install_dir, exist_ok=True)
            create_ini_separator_file(os.path.join(install_dir, 'meta.ini'))
            return

        # Find mod in mod make directive and install it if it exist
        m = self._find_mod_make_directive(name)
        if not m:
            return

        url = m['url']
        title = m['title']
        install_directives = m['install_directives']

        print(f'[+] Installing mod: {title}')

        # Downloading
        e = get_handler_for_url(url)
        filename = os.path.join(self._dl_dir, e.filename)
        if not os.path.isfile(filename):
            print(f'  - Downloading {e.filename}')
            e.download(filename)
        else:
            print(f'  - Using cached {e.filename}')

        os.makedirs(install_dir, exist_ok=True)
        with TemporaryDirectory(prefix="gamma-launcher-modinstall-") as dir:
            extract_archive(filename, dir)
            if not install_directives:
                copy_tree(dir, install_dir)
            else:
                # I'm a lazy bastard and I don't really get it.
                # Not gonna think about it all day, just do a quick & dirty 'trick'
                # But TODO: Fix this crap.
                for folder in ['fomod', 'gamedata']:
                    try:
                        copy_tree(
                            os.path.join(dir, folder),
                            os.path.join(install_dir, folder)
                        )
                    except DistutilsFileError:
                        pass

                for folder in install_directives:
                    # Can except if mod are updated (official launcher silently crash)
                    try:
                        print(f'    Installing {folder} -> {install_dir}')
                        copy_tree(os.path.join(dir, folder), install_dir)
                    except DistutilsFileError:
                        print(f'    ERROR: {folder} do not exist')

        create_ini_file(os.path.join(install_dir, 'meta.ini'), e.filename, url)

    def _install_mods(self) -> None:
        self._mods = self._read_mod_list()
        self._mods_make = self._read_mod_maker()

        for m in self._mods:
            self._install_mod(m)

    def _copy_gamma_modpack(self) -> None:
        path = os.path.join(self._grok_mod_dir, 'G.A.M.M.A', 'modpack_addons')
        print(f'[+] Copying G.A.M.M.A mods in from "{path}" to "{self._mod_dir}"')
        copy_tree(path, self._mod_dir)

    def _install_modorganizer_profile(self) -> None:
        p_path = os.path.join(self._gamma_dir, 'profiles', 'G.A.M.M.A')
        print(f'[+] Installing G.A.M.M.A profile in {p_path}')
        os.makedirs(p_path, exist_ok=True)
        copy2(
            os.path.join(self._grok_mod_dir, 'G.A.M.M.A', 'modpack_data', 'modlist.txt'),
            p_path
        )
        with open(os.path.join(p_path, 'settings.txt'), 'w') as f:
            f.write("""[General]
LocalSaves=false
LocalSettings=true
AutomaticArchiveInvalidation=false
""")

    def run(self, args):
        # Init paths
        self._anomaly_dir = args.anomaly
        self._gamma_dir = args.gamma

        self._dl_dir = os.path.join(args.gamma, "downloads")
        self._mod_dir = os.path.join(args.gamma, "mods")
        self._grok_mod_dir = os.path.join(args.gamma, ".Grok's Modpack Installer")

        # Start installing
        self._update_gamma_definition()
        self._patch_anomaly()
        self._install_mods()
        self._install_modorganizer_profile()
        self._copy_gamma_modpack()

        print('[+] Setup ended... Enjoy your journey in the Zone o/')
