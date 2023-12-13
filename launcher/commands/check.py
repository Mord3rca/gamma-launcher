from requests.exceptions import ConnectionError
from pathlib import Path
from os.path import sep
from typing import Iterator, Tuple

from launcher.commands.common import read_mod_maker, parse_moddb_data
from launcher.downloader import download_archive, HashError
from launcher.hash import check_hash


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
    def _read_checksums(anomaly: Path) -> Iterator[Tuple[Path, str]]:
        checksums = anomaly / "tools" / "checksums.md5"
        for line in checksums.read_text().split("\n"):
            if not line:
                continue
            hash, file = line.split(" ")
            file = anomaly / file.lstrip("*").replace("\\", sep)
            yield file, hash

    def run(self, args) -> None:
        anomaly = Path(args.anomaly)
        errors = []
        for file, hash in self._read_checksums(anomaly):
            if not check_hash(file, hash, desc=f"Checking Anomaly file: {file}..."):
                errors.append(str(file))

        if errors:
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

    def run(self, args) -> None:  # noqa: C901
        errors = []

        self._gamma = Path(args.gamma)
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
                errors.append(f"Can't fetch moddb page for {i['info_url']}\n  Reason: {e}")
                continue
            except KeyError:
                errors.append(f"Can't parse moddb page for {i['info_url']}")
                continue

            if info.get('Download', '') not in i['url']:
                errors.append(
                    f"Skipping {file.name} since ModDB info do not match download url"
                )
                continue

            if not file.exists() and not args.update_cache:
                errors.append(f"{file.name} not found on disk")
                continue

            if check_hash(file, hash):
                continue

            if not args.update_cache:
                errors.append(f"{file.name} MD5 missmatch")
                continue

            try:
                file = download_archive(i['url'], self._dl_dir, use_cached=False, hash=hash)
            except ConnectionError as e:
                errors.append(f"Failed to redownload {file.name}\n  Reason: {e}")
                continue
            except HashError:
                errors.append(f"{file.name} failed MD5 check after being redownloaded")
                continue

        if errors:
            raise HashError("\n".join(errors))
