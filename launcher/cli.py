from launcher import __title__, __version__
from launcher.commands import (
    AnomalyInstall,
    CheckAnomaly,
    CheckMD5,
    FullInstall,
    GammaSetup,
    RemoveReshade,
    PurgeShaderCache,
    TestModMaker,
    Usvfs,
)

from argparse import ArgumentParser, Namespace, SUPPRESS
from os import environ, execve, getenv
from pathlib import Path
from platformdirs import user_config_path
from sys import argv, platform, stderr

common_args = {
    "--anomaly": {
        "help": SUPPRESS,
    },
    "--cache-directory": {
        "help": SUPPRESS,
        "dest": "cache_path"
    },
    "--gamma": {
        "help": SUPPRESS,
    },
}


def command_object_to_dict(o):
    args = common_args.copy()
    args.update(o.arguments)
    return {
        o.name: {
            "help": o.help,
            "arguments": args,
            "cobject": o,
        }
    }


parser_desc = {
     "description": "Launcher for S.T.A.L.K.E.R.: G.A.M.M.A.",
     # Global arguments
     "arguments": {},
     "subparsers": {
         "help": "Command to invoke",
         "dest": "command",
         "list": {
             **command_object_to_dict(AnomalyInstall),
             **command_object_to_dict(CheckAnomaly),
             **command_object_to_dict(CheckMD5),
             **command_object_to_dict(FullInstall),
             **command_object_to_dict(GammaSetup),
             **command_object_to_dict(RemoveReshade),
             **command_object_to_dict(PurgeShaderCache),
             **command_object_to_dict(TestModMaker),
             **command_object_to_dict(Usvfs),
         },
     },
}


_config_file_path = user_config_path(__title__) / 'config.ini'
_no_config = getenv('GAMMA_LAUNCHER_NO_CONFIG') is not None


def save_configuration(args: Namespace) -> None:
    if _no_config:
        return

    # TODO: Smarter way ?
    save_str = ''
    if args.anomaly:
        save_str += f'--anomaly\n{args.anomaly}\n'
    if args.cache_path:
        save_str += f'--cache-directory\n{args.cache_path}\n'
    if args.gamma:
        save_str += f'--gamma\n{args.gamma}\n'

    _config_file_path.write_text(save_str)


def pyi_ssl_certs_workaround() -> None:
    # Will only run on linux if in a Pyinstaller context
    if not (platform == 'linux' or getenv("_PYI_ARCHIVE_FILE")):
        return

    if getenv('SSL_CERT_DIR') or getenv('SSL_CERT_FILE'):
        return

    ssl_files = (
        '/etc/ssl/certs/ca-certificates.crt',
        '/etc/pki/tls/certs/ca-bundle.crt',
        '/etc/ssl/ca-bundle.pem',
        '/etc/pki/tls/cacert.pem',
        '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem',
        '/etc/ssl/cert.pem',
    )
    ssl_dirs = (
        '/etc/ssl/certs',
        '/etc/tls/pki/certs',
    )

    for file in ssl_files:
        if Path(file).exists():
            environ.update({'SSL_CERT_FILE': file})
            execve(argv[0], argv, environ)

    for dir in ssl_dirs:
        if Path(dir).exists():
            environ.update({'SSL_CERT_DIR': dir})
            execve(argv[0], argv, environ)

    print(
        '[-] Lookup SSL Cert failed: In case of SSL errors during HTTPS transaction '
        'set SSL_CERT_DIR or SSL_CERT_FILE env variable.',
        file=stderr
    )


def main():
    pyi_ssl_certs_workaround()

    _config_file_path.parent.mkdir(parents=True, exist_ok=True)
    _config_file_path.touch(exist_ok=True)

    parser = ArgumentParser(description=parser_desc["description"], fromfile_prefix_chars='@')
    parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
    for m, a in parser_desc['arguments'].items():
        parser.add_argument(m, **a)

    subparsers = parser_desc['subparsers']
    sp = parser.add_subparsers(
        help=subparsers["help"], dest=subparsers["dest"]
    )
    sp.required = True

    for n, p in subparsers['list'].items():
        subparser = sp.add_parser(n, help=p['help'])
        for m, a in p["arguments"].items():
            subparser.add_argument(m, **a)
        subparser.set_defaults(cobject=p['cobject'])

    if len(argv) >= 2 and not _no_config:
        argv.insert(2, f'@{_config_file_path}')

    args = parser.parse_args()
    save_configuration(args)
    args.cobject().run(args)
