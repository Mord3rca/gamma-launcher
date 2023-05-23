from distutils.dir_util import copy_tree, DistutilsFileError
from pathlib import Path
from typing import Iterator


class Usvfs:

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
        gamma_dir = Path(args.gamma)
        anomaly_dir = Path(args.anomaly)
        install_dir = Path(args.final)

        install_dir.mkdir(parents=True)

        print('Copying Anomaly dir to install directory...')
        copy_tree(str(anomaly_dir), str(install_dir))

        print('Applying mods...')
        for mod in self._read_modlist(gamma_dir / 'profiles' / 'G.A.M.M.A' / 'modlist.txt'):
            print(f"  Installing {mod}")
            try:
                copy_tree(
                    str(gamma_dir / 'mods' / mod),
                    str(install_dir)
                )
            except DistutilsFileError as err:
                print(f"    --> Failed: {err}")

        print('Reapplying Anomaly binary dir to install directory')
        copy_tree(
            str(anomaly_dir / 'bin'),
            str(install_dir / 'bin')
        )
