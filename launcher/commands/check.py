from requests.exceptions import ConnectionError
from pathlib import Path
from os.path import sep

from launcher.commands.common import read_mod_maker, parse_moddb_data
from launcher.downloader import download_mod
from launcher.compat import file_digest


class CheckAnomaly:

    arguments: dict = {
        "--anomaly": {
            "help": "Path to Anomaly directory",
            "required": True,
            "type": str
        },
    }

    name: str = "check-anomaly"

    help: str = "Check Anomaly installation"

    @staticmethod
    def _read_checksums(anomaly: Path):
        checksums = anomaly / "tools" / "checksums.md5"
        for l in checksums.read_text().split("\n"):
            if(not l):
                continue
            hash, file = l.split(" ")
            file = anomaly / file.lstrip("*").replace("\\", sep)
            yield file, hash

    def run(self, args) -> None:
        anomaly = Path(args.anomaly)
        errors = []
        for file, hash in self._read_checksums(anomaly):
            print(f"Checking Anomaly file: {file}...")
            with file.open("rb") as f:
                fhash = file_digest(f, "md5").hexdigest()
            if(not fhash == hash):
                errors.append(str(file))

        if(errors):
            err_str = "\n".join(errors)
            raise RuntimeError(f"Invalid file(s) detected:\n{err_str}")


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

        try:
            file = download_mod(url, self._dl_dir, use_cached=False)
        except ConnectionError as e:
            self._register_err(f"Failed to download {file.name}\n  Reason: {e}")
            return

        if not self._test_hash(file, hash):
            self.register_err(f"Failed to download missing file - {file.name}")

    def run(self, args) -> None:  # noqa: C901
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
            except ConnectionError as e:
                self.register_err(f"Can't fetch moddb page for {i['info_url']}\n  Reason: {e}")
                continue
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

            try:
                file = download_mod(i['url'], self._dl_dir, use_cached=False)
            except ConnectionError as e:
                self._register_err(f"Failed to redownload {file.name}\n  Reason: {e}")
                continue

            if not self._test_hash(file, info['MD5 Hash']):
                self.register_err(f"{file.name} failed MD5 check after being redownloaded")

        for err in self._errors:
            print(err)
