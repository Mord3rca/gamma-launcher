from pathlib import Path
from shutil import copytree, rmtree
from typing import Iterator

from launcher.common import anomaly_arg, gamma_arg


class Usvfs:

    arguments: dict = {
        **anomaly_arg,
        **gamma_arg,
        "--final": {
            "help": "Path to final install directory",
            "required": True,
            "type": str
        },
    }

    name: str = "usvfs-workaround"

    help: str = "Workaround to use wine without ModOrganizer (& UserSpace Virtual FileSystem)"

    @staticmethod
    def _read_modlist(modlist: Path) -> Iterator[str]:
        mods = [
            i.lstrip('+') for i in filter(
               lambda x: x.startswith('+'), modlist.read_text().split('\n')
            )
        ]
        return reversed(mods)

    def run(self, args) -> None:
        gamma_dir = Path(args.gamma).expanduser()
        anomaly_dir = Path(args.anomaly).expanduser()
        install_dir = Path(args.final).expanduser()
        if install_dir.exists():
            print(f'Removing old directories from existing install {install_dir}')
            rmtree(install_dir / 'db', ignore_errors=True)
            rmtree(install_dir / 'gamedata', ignore_errors=True)
            rmtree(install_dir / 'appdata' / 'shaders_cache', ignore_errors=True)
        else:
            print('Fresh install')
            install_dir.mkdir(parents=True)

        print('Copying Anomaly dir to install directory...')
        copytree(anomaly_dir, install_dir, dirs_exist_ok=True)

        print('Applying mods...')
        for mod in self._read_modlist(gamma_dir / 'profiles' / 'G.A.M.M.A' / 'modlist.txt'):
            print(f"  Installing {mod}")
            try:
                copytree(gamma_dir / 'mods' / mod, install_dir, dirs_exist_ok=True)
            except FileNotFoundError as err:
                print(f"    --> Failed: {err}")

        print('Reapplying Anomaly binary dir to install directory')
        copytree(anomaly_dir / 'bin', install_dir / 'bin', dirs_exist_ok=True)
