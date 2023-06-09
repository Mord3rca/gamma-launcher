from pathlib import Path

from launcher.commands.common import read_mod_maker, parse_moddb_data
from launcher.downloader import download_mod
from launcher.compat import file_digest


class CheckMD5:

    arguments: dict = {
        "--gamma": {
            "help": "Path to GAMMA directory",
            "required": True,
            "type": str
        },
        "--update-cache": {
            "help": "Update download cache if file is missing or MD5 do not match",
            "required": False,
            "action": "store_true"
        },
        "--redownload": {
            "help": "Here for compatibility, same as --update-cache",
            "required": False,
            "dest": "update_cache",
            "action": "store_true"
        },
    }

    name: str = "check-md5"

    help: str = "Check MD5 hash for all addons"

    def __init__(self) -> None:
        self._gamma = None
        self._dl_dir = None
        self._errors = []
        self._update_cache = False

    def register_err(self, err: str, show: bool = True, level: str = "Error") -> None:
        self._errors += [f"{level}: {err}"]
        if show:
            print(f"  !! {err}")

    def _test_hash(self, file: Path, hash: str) -> bool:
        with open(file, 'rb') as f:
            md5 = file_digest(f, 'md5').hexdigest()

        valid = md5 == hash

        print(f"{file.name} ({hash}): ", end='')
        print("OK" if valid else "MISMATCH")

        return valid

    def _if_file_missing(self, file: Path, url: str, hash: str) -> None:
        if not self._update_cache:
            self.register_err(f"{file.name} not found on disk", show=False)
            return

        file = download_mod(url, self._dl_dir, use_cached=False)
        if not self._test_hash(file, hash):
            self.register_err(f"Failed to download missing file - {file.name}")

    def run(self, args) -> None:
        self._gamma = Path(args.gamma)
        self._update_cache = args.update_cache
        self._dl_dir = self._gamma / "downloads"
        modpack_data_dir = self._gamma / ".Grok's Modpack Installer" / "G.A.M.M.A" / "modpack_data"

        mod_maker = read_mod_maker(
            modpack_data_dir / 'modlist.txt',
            modpack_data_dir / 'modpack_maker_list.txt'
        )

        print('-- Starting MD5 Check')
        for i in filter(lambda v: v and v['info_url'], mod_maker.values()):
            try:
                info = parse_moddb_data(i['info_url'])
                file = self._dl_dir / info['Filename']
                hash = info['MD5 Hash']
            except KeyError:
                self.register_err(f"Can't parse moddb page for {i['info_url']}")
                continue

            if info.get('Download', '') not in i['url']:
                self.register_err(
                    f"Skipping {file.name} since ModDB info do not match download url",
                    show=False, level="Warning"
                )
                continue

            if not file.exists():
                self._if_file_missing(file, i['url'], hash)
                continue

            if self._test_hash(file, info['MD5 Hash']):
                continue

            if not args.update_cache:
                self.register_err(f"{file.name} MD5 missmatch")
                continue

            file = download_mod(i['url'], self._dl_dir, use_cached=False)
            if not self._test_hash(file, info['MD5 Hash']):
                self.register_err(f"{file.name} failed MD5 check after being redownloaded")

        for err in self._errors:
            print(err)
