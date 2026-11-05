from os import link
from pathlib import Path
from shutil import copy2, copytree
from typing import Iterator

from launcher.common import anomaly_arg, gamma_arg


def _copy(src: str, dst: str) -> None:
    Path(dst).unlink(missing_ok=True)
    copy2(src, dst)


def _link(src: str, dst: str) -> None:
    Path(dst).unlink(missing_ok=True)
    try:
        link(src, dst)
    except OSError:
        copy2(src, dst)


class Usvfs:

    arguments: dict = {
        **anomaly_arg,
        **gamma_arg,
        "--final": {
            "help": "Path to final install directory",
            "required": True,
            "type": str
        },
        "--hardlink": {
            "help": "Hard link files instead of copying them (files edited in place are shared with Anomaly & mods)",
            "action": "store_true",
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
        install_file = _link if args.hardlink else _copy

        install_dir.mkdir(parents=True, exist_ok=True)

        print('Copying Anomaly dir to install directory...')
        copytree(anomaly_dir, install_dir, copy_function=install_file, dirs_exist_ok=True)

        print('Applying mods...')
        for mod in self._read_modlist(gamma_dir / 'profiles' / 'G.A.M.M.A' / 'modlist.txt'):
            print(f"  Installing {mod}")
            try:
                copytree(gamma_dir / 'mods' / mod, install_dir, copy_function=install_file, dirs_exist_ok=True)
            except FileNotFoundError as err:
                print(f"    --> Failed: {err}")

        print('Reapplying Anomaly binary dir to install directory')
        copytree(anomaly_dir / 'bin', install_dir / 'bin', copy_function=install_file, dirs_exist_ok=True)
