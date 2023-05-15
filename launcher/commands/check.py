from hashlib import file_digest
from pathlib import Path

from launcher.commands.common import read_mod_maker, parse_moddb_data
from launcher.downloader import _download_mod


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
        for k, v in filter(lambda x: x[1] and x[1]["info_url"], mod_maker.items()):
            try:
                info = parse_moddb_data(v['info_url'])
                file = modpack_dl_dir / info['Filename']
            except KeyError:
                print(f"  !! Can't parse moddb page for {v['info_url']}")
                errors += [f"Error: parsing failure for {v['info_url']}"]
                continue

            if info.get('Download', '') not in v['url']:
                errors += [f"WARNING: Skipping {file.name} since ModDB info do not match download url"]
                continue

            if not file.exists():
                errors += [f"Error: {file.name} not found on disk"]
                continue

            with open(file, 'rb') as f:
                md5 = file_digest(f, 'md5').hexdigest()
            print(f"{file.name} remote hash is: '{info['MD5 Hash']}'")
            print(f"{file.name} local  hash is: '{md5}'")

            if md5 != info['MD5 Hash']:
                errors += [f"Error: {file.name} -- remote({info['MD5 Hash']}) != local({md5})"]
                if redownload:
                    print(f"Redownloading {file.name}...")
                    if self.redownload(v, args.gamma):
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

    def redownload(self, dict: dict, gamma_dir: str) -> bool:
        """
        Downloads and installs a specific mod, then checks its MD5 hash again.

        :param dict:
        Values gathered from the modpack_maker_list.txt file.
        :param gamma_dir:
        Path to the GAMMA folder.

        :return:
        Whether the local and remote MD5 hashes match.
        """

        # Download and install the mod:
        download_dir = Path(gamma_dir).joinpath("downloads")
        file = _download_mod(dict["url"], download_dir, use_cached=False)

        # Check MD5 sum again:
        info = parse_moddb_data(dict["info_url"])
        with open(file, 'rb') as f:
            local_md5 = file_digest(f, 'md5').hexdigest()
        print(f"{info['Filename']} remote hash is: '{info['MD5 Hash']}'")
        print(f"{info['Filename']} local  hash is: '{local_md5}'")

        return info["MD5 Hash"] == local_md5
