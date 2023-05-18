from distutils.dir_util import copy_tree, DistutilsFileError
from pathlib import Path
from shutil import copy2, move
from tempfile import TemporaryDirectory

from launcher.downloader import download_mod
from launcher.archive import extract_archive
from launcher.downloader import get_handler_for_url
from launcher.meta import create_ini_file, create_ini_separator_file

from .common import read_mod_maker


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
        "--no-def-update": {
            "help": "Do not update S.T.A.L.K..E.R.: G.A.M.M.A. definition",
            "action": "store_false",
            "dest": "update_def",
        },
        "--no-anomaly-patch": {
            "help": "Do not patch Anomaly directory",
            "action": "store_false",
            "dest": "anomaly_patch",
        },
        "--preserve-user-config": {
            "help": "Do not overwrite user configuration when patching Anomaly directory",
            "action": "store_true",
        },
    }

    name: str = "full-install"

    help: str = "Complete install of S.T.A.L.K.E.R.: G.A.M.M.A."

    def __init__(self):
        self._anomaly_dir = None
        self._gamma_dir = None

        self._dl_dir = None
        self._mod_dir = None
        self._grok_mod_dir = None

        self._mods_make = {}

    def _update_gamma_definition(self) -> None:
        print('[+] Updating G.A.M.M.A. definition')
        gdef = self._grok_mod_dir / 'GAMMA_definition.zip'

        if not gdef.is_file():
            print('    downloading archive...')
            g = get_handler_for_url("https://github.com/Grokitach/Stalker_GAMMA/archive/refs/heads/main.zip")
            g.download(gdef)

        with TemporaryDirectory(prefix="gamma-launcher-") as dir:
            extract_archive(gdef, dir)
            copy_tree(
                str(Path(dir) / 'Stalker_GAMMA-main'),
                str(self._grok_mod_dir)
            )

        move(
            self._grok_mod_dir / 'G.A.M.M.A_definition_version.txt',
            self._grok_mod_dir / 'version.txt'
        )

    def _patch_anomaly(self, preserve_user_config: bool = False) -> None:
        user_config = self._anomaly_dir / 'appdata' / 'user.ltx'
        saved_config = self._anomaly_dir / 'appdata' / 'user.ltx.bak'

        if user_config.is_file():
            copy2(user_config, saved_config)

        copy_tree(
            str(self._grok_mod_dir / 'G.A.M.M.A' / 'modpack_patches'),
            str(self._anomaly_dir)
        )

        if preserve_user_config:
            copy2(saved_config, user_config)

    def _install_mod(self, name: str, m: dict) -> None:
        install_dir = self._mod_dir / name

        # Special case, it's a separator
        if 'separator' in name:
            print(f'[+] Installing separator: {name}')
            install_dir.mkdir(exist_ok=True)
            create_ini_separator_file(install_dir / 'meta.ini')
            return

        if not m:
            return

        url = m['url']
        title = m['title']
        install_directives = m['install_directives']

        print(f'[+] Installing mod: {title}')

        file = download_mod(url, self._dl_dir)

        install_dir.mkdir(exist_ok=True)
        with TemporaryDirectory(prefix="gamma-launcher-modinstall-") as dir:
            extract_archive(file, dir)
            if not install_directives:
                copy_tree(dir, str(install_dir))
            else:
                # I'm a lazy bastard and I don't really get it.
                # Not gonna think about it all day, just do a quick & dirty 'trick'
                # But TODO: Fix this crap.
                for folder in ['fomod', 'gamedata']:
                    try:
                        copy_tree(
                            str(Path(dir) / folder),
                            str(install_dir / folder)
                        )
                    except DistutilsFileError:
                        pass

                for folder in install_directives:
                    # Can except if mod are updated (official launcher silently crash)
                    try:
                        print(f'    Installing {folder} -> {install_dir}')
                        copy_tree(str(Path(dir) / folder), str(install_dir))
                    except DistutilsFileError:
                        print(f'    WARNING: {folder} does not exist')

        create_ini_file(install_dir / 'meta.ini', file.name, url)

    def _install_mods(self) -> None:
        self._mods_make = read_mod_maker(
            self._grok_mod_dir / 'G.A.M.M.A' / 'modpack_data' / 'modlist.txt',
            self._grok_mod_dir / 'G.A.M.M.A' / 'modpack_data' / 'modpack_maker_list.txt'
        )

        for k, v in self._mods_make.items():
            self._install_mod(k, v)

    def _copy_gamma_modpack(self) -> None:
        path = self._grok_mod_dir / 'G.A.M.M.A' / 'modpack_addons'
        print(f'[+] Copying G.A.M.M.A mods in from "{path}" to "{self._mod_dir}"')
        copy_tree(str(path), str(self._mod_dir))

    def _install_modorganizer_profile(self) -> None:
        p_path = self._gamma_dir / 'profiles' / 'G.A.M.M.A'
        settings = p_path / 'settings.txt'

        print(f'[+] Installing G.A.M.M.A profile in {p_path}')
        p_path.mkdir(exist_ok=True)
        copy2(
            self._grok_mod_dir / 'G.A.M.M.A' / 'modpack_data' / 'modlist.txt',
            p_path
        )
        settings.write_text("""[General]
LocalSaves=false
LocalSettings=true
AutomaticArchiveInvalidation=false
""")

    def run(self, args):
        # Init paths
        self._anomaly_dir = Path(args.anomaly)
        self._gamma_dir = Path(args.gamma)

        self._dl_dir = Path(args.gamma) / "downloads"
        self._mod_dir = Path(args.gamma) / "mods"
        self._grok_mod_dir = Path(args.gamma) / ".Grok's Modpack Installer"

        # Start installing
        if args.update_def:
            self._update_gamma_definition()
        if args.anomaly_patch:
            self._patch_anomaly(args.preserve_user_config)

        self._install_mods()
        self._install_modorganizer_profile()
        self._copy_gamma_modpack()

        print('[+] Setup ended... Enjoy your journey in the Zone o/')
