from distutils.dir_util import copy_tree
from os import name as os_name
from pathlib import Path
from requests.exceptions import ConnectionError
from shutil import copy2, disk_usage, move
from sys import exit
from tempfile import TemporaryDirectory
from typing import Dict, List

from launcher.commands import CheckAnomaly
from launcher.downloader import download_archive, download_mod
from launcher.downloader.base import g_session
from launcher.archive import extract_archive
from launcher.downloader import get_handler_for_url
from launcher.meta import create_ini_file, create_ini_separator_file

from .common import read_mod_maker, parse_moddb_data


guide_url: str = "https://github.com/DravenusRex/stalker-gamma-linux-guide"


class AnomalyInstall:

    arguments: dict = {
        "--anomaly": {
            "help": "Path to ANOMALY directory",
            "required": True,
            "type": str
        },
        "--anomaly-skip-verify": {
            "help": "Skip installation verification",
            "action": "store_false",
            "dest": "anomaly_verify"
        },
        "--anomaly-purge-cache": {
            "help": "Do not keep 7z archives",
            "action": "store_true",
            "dest": "anomaly_purge_cache"
        },
        "--cache-directory": {
            "help": "Path to cache directory",
            "type": str,
            "dest": "cache_path"
        },
    }

    name: str = "anomaly-install"

    help: str = "Installation of S.T.A.L.K.E.R.: Anomaly"

    files: Dict[str, Dict[str, str]] = {
        "base-1.5.1": {
            "dl_link": "https://www.moddb.com/downloads/start/207799",
            "moddb_page": "https://www.moddb.com/mods/stalker-anomaly/downloads/stalker-anomaly-151",
        },
        "update-1.5.2": {
            "dl_link": "https://www.moddb.com/downloads/start/235237",
            "moddb_page": "https://www.moddb.com/mods/stalker-anomaly/downloads/stalker-anomaly-151-to-152",
        },
    }

    def __init__(self) -> None:
        self._anomaly_dir = None
        self._cache_dir = None

    def _dl_component(self, c_data: Dict) -> Path:
        metadata = parse_moddb_data(c_data.get("moddb_page"))
        return download_archive(c_data.get("dl_link"), self._cache_dir, hash=metadata.get('MD5 Hash'))

    def _install_component(self, comp: str, ext: str = None) -> None:
        c = self.files.get(comp)
        file = self._dl_component(c)

        print("  - Extracting")
        extract_archive(file, self._anomaly_dir, ext)

    def _purge_cache(self) -> None:
        print("[+] Purging Anomaly archives")
        for archive in self._anomaly_dir.glob("*.7z"):
            archive.unlink()

    def run(self, args) -> None:
        self._anomaly_dir = Path(args.anomaly)
        self._anomaly_dir.mkdir(parents=True, exist_ok=True)

        self._cache_dir = Path(args.cache_path or args.anomaly)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        print("[+] Installing base Anomaly 1.5.1")
        self._install_component("base-1.5.1", ext="7z-bcj2")

        print("[+] Installing update Anomaly 1.5.1 to 1.5.2")
        self._install_component("update-1.5.2", ext="7z-bcj2")

        if (args.anomaly_verify):
            CheckAnomaly().run(args)

        if (args.anomaly_purge_cache):
            self._purge_cache()


class GammaSetup:

    arguments: dict = {
        "--gamma": {
            "help": "Path to GAMMA directory",
            "required": True,
            "type": str
        },
        "--gamma-no-mod-organizer": {
            "help": "Skip ModOrganizer installation",
            "action": "store_false",
            "dest": "gamma_install_mo",
        },
        "--gamma-set-mod-organizer-version": {
            "help": "Set ModOrganizer Version (have to match github tags)",
            "type": str,
            "default": "v2.4.4",
            "dest": "mo_version",
        },
        "--cache-directory": {
            "help": "Path to cache directory",
            "type": str,
            "dest": "cache_path"
        },
    }

    name: str = "gamma-setup"

    help: str = "Preliminary setup for S.T.A.L.K.E.R.: G.A.M.M.A."

    def __init__(self) -> None:
        self._cache_dir = None
        self._gamma_dir = None
        self._grok_mod_dir = None

    def _check_tmp_free_space(self, size=5*1024*1024*1024) -> None:
        with TemporaryDirectory(prefix="gamma-launcher-mo-setup-") as dir:
            _, __, free = disk_usage(dir)
            if free < size:
                raise RuntimeError(
                    "You need at least 5 GiB of space in TMPDIR for this to work.\n"
                    "Please export TMPDIR to a folder with enough space available."
                )

    def _install_mod_organizer(self, version: str) -> None:
        url = "https://github.com/ModOrganizer2/modorganizer/releases/download/" + \
              f"{version}/Mod.Organizer-{version.lstrip('v')}.7z"

        with TemporaryDirectory(prefix="gamma-launcher-mo-setup-") as dir:
            mo_archive = download_archive(url, self._cache_dir or dir, host='base')
            extract_archive(mo_archive, self._gamma_dir)

    def run(self, args) -> None:
        if not args.cache_path:
            self._check_tmp_free_space()

        self._gamma_dir = Path(args.gamma)
        self._grok_mod_dir = Path(args.gamma) / ".Grok's Modpack Installer" / "G.A.M.M.A"
        self._grok_mod_dir.mkdir(parents=True, exist_ok=True)

        if args.cache_path:
            self._cache_dir = Path(args.cache_path)
            self._cache_dir.mkdir(parents=True, exist_ok=True)

        print("[+] Installing base setup for GAMMA")
        if args.gamma_install_mo:
            self._install_mod_organizer(args.mo_version)

        with TemporaryDirectory(prefix="gamma-launcher-mo-setup-") as dir:
            file = download_archive("https://github.com/Grokitach/gamma_setup", self._cache_dir or dir)
            extract_archive(file, self._grok_mod_dir)

        gamma_setup_dir = list(self._grok_mod_dir.glob("gamma_setup-*"))[0]
        for i in gamma_setup_dir.glob("*"):
            move(i, self._grok_mod_dir)
        gamma_setup_dir.rmdir()

        for i in ["downloads", "mods"]:
            (self._gamma_dir / i).mkdir(exist_ok=True)


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

    folder_to_install: List[str] = ['appdata', 'bin', 'db', 'gamedata']

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

        try:
            l_version = Path(self._grok_mod_dir / 'version.txt').read_text().strip()
            r_version = g_session.get(
                'https://raw.githubusercontent.com/Grokitach/Stalker_GAMMA/main/G.A.M.M.A_definition_version.txt'
            ).text.strip()
            if int(r_version) > int(l_version):
                gdef.unlink()
                print(f"    will be updated from {l_version} to {r_version}")
        except Exception:
            pass

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

    def _fix_path_case(self, dir: Path) -> None:
        # Do not exec this on windows
        if os_name == 'nt':
            return

        for path in filter(
            lambda x: x.name.lower() in self.folder_to_install and x.name != x.name.lower(),
            dir.glob('**')
        ):
            for file in path.glob('**/*.*'):
                t = file.relative_to(path.parent)
                rp = str(t.parent).lower()
                nfolder = path.parent / rp
                nfolder.mkdir(parents=True, exist_ok=True)
                file.rename(nfolder / file.name)

    def _fix_malformed_archive(self, dir: Path) -> None:
        # Do not exec this on windows
        if os_name == 'nt':
            return

        for path in dir.glob('*.*'):
            if '\\' not in path.name:
                continue

            p = dir / path.name.replace('\\', '/')
            p.parent.mkdir(parents=True, exist_ok=True)
            path.rename(dir / p)

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

        try:
            file = download_mod(url, self._dl_dir)
        except ConnectionError as e:
            print(f"[-] Failed to download {url} for {title}\n  Reason: {e}")
            return

        install_dir.mkdir(exist_ok=True)
        with TemporaryDirectory(prefix="gamma-launcher-modinstall-") as dir:
            pdir = Path(dir)
            extract_archive(file, dir)
            self._fix_malformed_archive(pdir)
            self._fix_path_case(pdir)

            iterator = [pdir] + ([Path(dir) / i for i in install_directives] if install_directives else [])
            for i in iterator:
                if pdir != i:
                    print(f'    Installing {i.name} -> {install_dir}')

                if not i.exists():
                    print(f'    WARNING: {i.name} does not exist')

                # Well, I guess it's a feature now.
                # Maybe I'm not that lazy after all
                for gamedir in self.folder_to_install:
                    pgame_dir = i / gamedir

                    if not pgame_dir.exists():
                        continue

                    copy_tree(
                        str(pgame_dir),
                        str(install_dir / gamedir)
                    )

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
        p_path.mkdir(parents=True, exist_ok=True)
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

        # Make sure folder are existing
        self._dl_dir.mkdir(parents=True, exist_ok=True)

        if not (self._anomaly_dir / "bin").is_dir():
            print(
                f"Follow this installation guide: {guide_url}\n"
                "And make sure Anomaly is correctly installed."
            )
            exit(1)

        if not (self._mod_dir.is_dir() and self._grok_mod_dir.is_dir()):
            print(
                f"Follow this installation guide: {guide_url}\n"
                "And make sure GAMMA RC3 is correctly installed."
            )
            exit(1)

        # Start installing
        if args.update_def:
            self._update_gamma_definition()
        if args.anomaly_patch:
            self._patch_anomaly(args.preserve_user_config)

        self._install_mods()
        self._install_modorganizer_profile()
        self._copy_gamma_modpack()

        print('[+] Setup ended... Enjoy your journey in the Zone o/')
