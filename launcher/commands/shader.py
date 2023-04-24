from os import remove
from shutil import rmtree
from pathlib import Path


class RemoveReshade:

    name: str = 'remove_reshade'

    help: str = 'Remove ReShade from Anomaly bin'

    arguments: dict = {
        "--anomaly": {
            "help": "Path to ANOMALY directory",
            "required": True,
            "type": str
        }
    }

    def run(self, args) -> None:
        anomaly = Path(args.anomaly)
        bin_files = [
            'd3d9.dll', 'dxgi.dll', 'dxgi.log',
            'G.A.M.M.A.Reshade.ini', 'ReShade.ini',
            'ReShade.log', 'reshade-shaders'
        ]

        for i in bin_files:
            file = anomaly / 'bin' / i

            if not file.exists():
                continue

            func = rmtree if file.is_dir() else remove
            func(file)
