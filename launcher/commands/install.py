from distutils.dir_util import copy_tree
from pathlib import Path
from shutil import copy2, disk_usage, move
from tempfile import TemporaryDirectory
from typing import Dict

from launcher.commands import CheckAnomaly
from launcher.common import anomaly_arg, gamma_arg, cache_dir_arg
from launcher.mods.downloader import g_session

from launcher.mods import BaseArchive, GithubArchive, ModDBArchive, read_mod_maker


guide_url: str = "https://github.com/DravenusRex/stalker-gamma-linux-guide"


def check_tmp_free_space(size: int) -> None:
    with TemporaryDirectory() as dir:
        _, __, free = disk_usage(dir)
        if free < (size * 1024 * 1024 * 1024):
            raise RuntimeError(
                f"You need at least {size} GiB of space in TMPDIR for this to work.\n"
                "Please export TMPDIR to a folder with enough space available."
            )


class AnomalyInstall:

    arguments: dict = {
        **anomaly_arg,
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
        **cache_dir_arg,
    }

    name: str = "anomaly-install"

    help: str = "Installation of S.T.A.L.K.E.R.: Anomaly"

    def __init__(self) -> None:
        self._anomaly_dir = None
        self._cache_dir = None

    def run(self, args) -> None:
        self._anomaly_dir = Path(args.anomaly)
        self._anomaly_dir.mkdir(parents=True, exist_ok=True)

        self._cache_dir = Path(args.cache_path or args.anomaly)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        print("[+] Installing base Anomaly 1.5.1")
        mod_base = ModDBArchive(
            "base-1.5.1", "https://www.moddb.com/downloads/start/207799",
            "https://www.moddb.com/mods/stalker-anomaly/downloads/stalker-anomaly-151"
        )
        mod_base.download(self._cache_dir, use_cached=True)
        print("  - Extracting")
        mod_base.install(self._anomaly_dir)

        print("[+] Installing update Anomaly 1.5.1 to 1.5.2")
        mod_update = ModDBArchive(
            "update-1.5.2", "https://www.moddb.com/downloads/start/235237",
            "https://www.moddb.com/mods/stalker-anomaly/downloads/stalker-anomaly-151-to-152"
        )
        mod_update.download(self._cache_dir, use_cached=True)
        print("  - Extracting")
        mod_update.install(self._anomaly_dir)

        if (args.anomaly_verify):
            CheckAnomaly().run(args)

        if (args.anomaly_purge_cache):
            print("[+] Purging Anomaly archives")
            mod_base.archive.unlink()
            mod_update.archive.unlink()


class GammaSetup:

    arguments: dict = {
        **gamma_arg,
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
        **cache_dir_arg,
    }

    name: str = "gamma-setup"

    help: str = "Preliminary setup for S.T.A.L.K.E.R.: G.A.M.M.A."

    def __init__(self) -> None:
        self._cache_dir = None
        self._gamma_dir = None
        self._grok_mod_dir = None

    def _install_mod_organizer(self, version: str) -> None:
        url = "https://github.com/ModOrganizer2/modorganizer/releases/download/" + \
              f"{version}/Mod.Organizer-{version.lstrip('v')}.7z"

        with TemporaryDirectory(prefix="gamma-launcher-mo-setup-") as dir:
            mo_archive = BaseArchive(url)
            mo_archive.download(Path(self._cache_dir or dir), use_cached=True)
            mo_archive.extract(self._gamma_dir)

    def run(self, args) -> None:
        if not args.cache_path:
            check_tmp_free_space(5)

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
            archive = GithubArchive("https://github.com/Grokitach/gamma_setup")
            archive.download(Path(self._cache_dir or dir), True)
            archive.extract(self._grok_mod_dir, "gamma_setup-*")

        downloads_dir = self._gamma_dir / "downloads"
        if args.cache_path:
            downloads_dir.rmdir()
            downloads_dir.symlink_to(self._cache_dir.absolute(), target_is_directory=True)
        else:
            downloads_dir.mkdir(exist_ok=True)

        (self._gamma_dir / "mods").mkdir(exist_ok=True)


def _create_full_install_args() -> Dict:
    arguments: dict = {}
    arguments.update(AnomalyInstall.arguments)
    arguments.update(GammaSetup.arguments)
    arguments.update({
        "--custom-gamma-definition": {
            "help": "Set a custom revision for S.T.A.L.K..E.R.: G.A.M.M.A.",
            "type": str,
            "dest": "custom_def",
            "default": None,
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
    })

    return arguments


class FullInstall:

    arguments: dict = _create_full_install_args()

    name: str = "full-install"

    help: str = "Complete install of S.T.A.L.K.E.R.: G.A.M.M.A."

    def __init__(self):
        self._anomaly_dir = None
        self._gamma_dir = None

        self._dl_dir = None
        self._mod_dir = None
        self._grok_mod_dir = None

    def _update_gamma_definition(self, *args) -> None:
        print('[+] Updating G.A.M.M.A. definition')
        gdef = self._grok_mod_dir / 'GAMMA_definition.zip'

        try:
            l_version = Path(self._grok_mod_dir / 'version.txt').read_text().strip()
            if 'Custom' in l_version:
                print('  -> Skipped since version is set to a custom one.')
                return

            r_version = g_session.get(
                'https://raw.githubusercontent.com/Grokitach/Stalker_GAMMA/main/G.A.M.M.A_definition_version.txt'
            ).text.strip()
            if int(r_version) > int(l_version):
                gdef.unlink()
                print(f"    will be updated from {l_version} to {r_version}")
        except Exception:
            pass

        g = GithubArchive('https://github.com/Grokitach/Stalker_GAMMA')
        print('    downloading archive...')
        g.download(self._grok_mod_dir, filename='GAMMA_definition.zip', use_cached=True)
        g.extract(self._grok_mod_dir, 'Stalker_GAMMA-main')

        move(
            self._grok_mod_dir / 'G.A.M.M.A_definition_version.txt',
            self._grok_mod_dir / 'version.txt',
        )

    def _set_custom_gamma_def(self, rev: str) -> None:
        print(f'[+] Setting custom G.A.M.M.A. definition to: {rev}')

        g = GithubArchive(f'https://github.com/Grokitach/Stalker_GAMMA/archive/{rev}.zip')
        g.download(self._grok_mod_dir, filename='GAMMA_definition.zip')
        g.extract(self._grok_mod_dir, '*')

        (self._grok_mod_dir / 'G.A.M.M.A_definition_version.txt').unlink()
        (self._grok_mod_dir / 'version.txt').write_text(f'Custom: {rev}\n')

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

    def _install_mods(self) -> None:
        for mod in read_mod_maker(self._grok_mod_dir / 'G.A.M.M.A' / 'modpack_data'):
            if mod.name == "164- Hunger Thirst Sleep UI 0.71 - xcvb":
                continue
            mod.download(self._dl_dir, use_cached=True)
            mod.install(self._mod_dir)

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
        check_tmp_free_space(6)

        # Init paths
        self._anomaly_dir = Path(args.anomaly)
        self._gamma_dir = Path(args.gamma)

        self._dl_dir = Path(args.gamma) / "downloads"
        self._mod_dir = Path(args.gamma) / "mods"
        self._grok_mod_dir = Path(args.gamma) / ".Grok's Modpack Installer"

        # Make sure folder are existing
        self._dl_dir.mkdir(parents=True, exist_ok=True)

        if not (self._anomaly_dir / "bin").is_dir():
            AnomalyInstall().run(args)

        if not (self._mod_dir.is_dir() and self._grok_mod_dir.is_dir()):
            GammaSetup().run(args)

        # Start installing
        if args.update_def:
            (self._update_gamma_definition if not args.custom_def else self._set_custom_gamma_def)(args.custom_def)
        if args.anomaly_patch:
            self._patch_anomaly(args.preserve_user_config)

        self._install_mods()
        self._install_modorganizer_profile()
        self._copy_gamma_modpack()

        print('[+] Setup ended... Enjoy your journey in the Zone o/')
