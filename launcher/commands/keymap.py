from pathlib import Path
from sys import exit

from launcher.common import anomaly_arg
from launcher.userltx import UserLTX


class SwitchKeymap:

    name: str = 'switch-keymap'

    help: str = 'Switch keymap of user.ltx from QWERTY to AZERTY layout'

    arguments: dict = {
        **anomaly_arg,
        '--to-dvorak': {
            'help': 'Use DVORAK instead of AZERTY',
            'action': 'store_const',
            'const': 'dvorak',
            'dest': 'layout',
            'default': 'azerty',
        }
    }

    def run(self, args) -> None:
        anomaly = Path(args.anomaly).expanduser()

        with UserLTX(anomaly / 'appdata' / 'user.ltx') as cfg:
            if cfg.bind['forward'] != 'kW':
                print('[-] user.ltx does not seems to be in QWERTY ... Aborting')
                exit(1)

            getattr(cfg.bind, f'to_{args.layout}_layout')()
