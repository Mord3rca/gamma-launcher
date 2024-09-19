from typing import Tuple

folder_to_install: Tuple[str] = ('appdata', 'db', 'gamedata')

anomaly_arg = {
    "--anomaly": {
        "help": "Path to ANOMALY directory",
        "required": True,
        "type": str
    }
}

gamma_arg = {
    "--gamma": {
        "help": "Path to GAMMA directory",
        "required": True,
        "type": str
    }
}

cache_dir_arg = {
    "--cache-directory": {
        "help": "Path to cache directory",
        "type": str,
        "dest": "cache_path"
    }
}
