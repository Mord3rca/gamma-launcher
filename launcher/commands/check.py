import sys

from argparse import SUPPRESS
from pathlib import Path
from os.path import sep
from typing import Iterator, Tuple

from launcher.common import anomaly_arg, gamma_arg
from launcher.hash import check_hash
from launcher.mods import read_mod_maker
from launcher.exceptions import HashError, ModDBDownloadError


class CheckAnomaly:

    arguments: dict = {
        **anomaly_arg
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
        anomaly = Path(args.anomaly).expanduser()
        errors = []
        for file, hash in self._read_checksums(anomaly):
            if not check_hash(file, hash, desc=f"Checking Anomaly file: {file}..."):
                errors.append(str(file))

        if errors:
            err_str = "\n".join(errors)
            raise RuntimeError(f"Invalid file(s) detected:\n{err_str}")


class CheckMD5:

    arguments: dict = {
        **gamma_arg,
        "--update-cache": {
            "help": "Update download cache if file is missing or MD5 do not match",
            "required": False,
            "action": "store_true"
        },
        "--redownload": {
            "help": SUPPRESS,
            "required": False,
            "dest": "update_cache",
            "action": "store_true"
        },
    }

    name: str = "check-md5"

    help: str = "Check MD5 hash for all addons"

    def run(self, args) -> None:
        errors = []

        gamma = Path(args.gamma).expanduser()
        dl_dir = gamma / "downloads"

        mod_maker = read_mod_maker(
            gamma / ".Grok's Modpack Installer" / "G.A.M.M.A" / "modpack_data"
        )

        print('-- Starting MD5 Check')
        for i in mod_maker:
            try:
                i.check(dl_dir, args.update_cache)
            except (HashError, ModDBDownloadError) as e:
                errors.append(str(e))

        print("\n".join(errors))

        sys.exit(0 if not errors else 1)
