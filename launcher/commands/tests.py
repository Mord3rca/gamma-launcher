from pathlib import Path
from typing import Dict

from launcher.archive import list_archive_content
from launcher.commands.common import read_mod_maker
from launcher.downloader import get_handler_for_url


class TestModMaker:

    arguments: dict = {
        "--gamma": {
            "help": "Path to GAMMA directory",
            "required": True,
            "type": str
        },
    }

    name: str = "test-mod-maker"

    help: str = "Testing mod maker directives"

    def __init__(self):
        self.modpack_dl_dir = None
        self.modpack_data_dir = None

    def _check_install_directives(self, mod: Dict):
        if not mod['install_directives']:
            return

        e = get_handler_for_url(mod['url'])
        archive = self.modpack_dl_dir / e.filename

        if not archive.exists():
            print(f"Downloading missing file: {archive.name}")
            e.download(archive)

        content = list_archive_content(archive)
        if not content:
            print(f"WARNING: {archive.name} is empty")
            return

        for d in mod['install_directives']:
            for f in content:
                if d in f:
                    break
            else:
                print(f'Warning: "{d}" is not in "{archive.name}"')

    def run(self, args) -> None:
        self.modpack_dl_dir = Path(args.gamma) / "downloads"
        self.modpack_data_dir = Path(args.gamma) / ".Grok's Modpack Installer" / "G.A.M.M.A" / "modpack_data"

        mod_maker = read_mod_maker(
            self.modpack_data_dir / 'modlist.txt',
            self.modpack_data_dir / 'modpack_maker_list.txt'
        )

        for mod in filter(lambda x: x, mod_maker.values()):
            self._check_install_directives(mod)
