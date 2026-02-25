from typing import Tuple

folder_to_install: Tuple[str] = ('appdata', 'db', 'gamedata')
"Folder to lookout for GAMMA mods installation"

anomaly_arg = {
    "--anomaly": {
        "help": "Path to ANOMALY directory",
        "required": True,
        "type": str
    }
}
"Common arg(s) for Anomaly commands"

gamma_arg = {
    "--gamma": {
        "help": "Path to GAMMA directory",
        "required": True,
        "type": str
    }
}
"Common arg(s) for GAMMA commands"

cache_dir_arg = {
    "--cache-directory": {
        "help": "Path to cache directory",
        "type": str,
        "dest": "cache_path"
    }
}
"Common arg(s) for cache directory function"
