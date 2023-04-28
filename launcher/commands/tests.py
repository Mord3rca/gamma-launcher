import os.path

from pathlib import Path

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

    def run(self, args) -> None:
        modpack_dl_dir = Path(args.gamma) / "downloads"
        modpack_data_dir = Path(args.gamma) / ".Grok's Modpack Installer" / "G.A.M.M.A" / "modpack_data"

        mod_maker = read_mod_maker(
            modpack_data_dir / 'modlist.txt',
            modpack_data_dir / 'modpack_maker_list.txt'
        )

        for i in filter(lambda v: v and v['install_directives'], mod_maker.values()):
            e = get_handler_for_url(i['url'])
            archive = modpack_dl_dir / e.filename

            if not archive.exists():
                print(f"Downloading missing file: {archive.name}")
                e.download(archive)

            content = [i.strip(os.path.sep) for i in list_archive_content(archive)]
            if not content:
                print(f"WARNING: {archive.name} is empty")
                continue

            for d in i['install_directives']:
                if d not in content:
                    print(f'Warning: "{d}" is not in "{archive.name}"')
