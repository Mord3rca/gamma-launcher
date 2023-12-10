from launcher.__version__ import __version__
from launcher.commands import (
    AnomalyInstall,
    CheckMD5,
    FullInstall,
    RemoveReshade,
    PurgeShaderCache,
    TestModMaker,
    Usvfs,
)

from argparse import ArgumentParser


def command_object_to_dict(o):
    return {
        o.name: {
            "help": o.help,
            "arguments": o.arguments,
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
             **command_object_to_dict(CheckMD5),
             **command_object_to_dict(FullInstall),
             **command_object_to_dict(RemoveReshade),
             **command_object_to_dict(PurgeShaderCache),
             **command_object_to_dict(TestModMaker),
             **command_object_to_dict(Usvfs),
         },
     },
}


def main():
    global parser_desc

    parser = ArgumentParser(description=parser_desc["description"])
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

    args = parser.parse_args()
    args.cobject().run(args)
