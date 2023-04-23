from launcher.commands import FullInstall

from argparse import ArgumentParser


def main():
    parser = ArgumentParser(
        description="Setting up S.T.A.L.K.E.R. G.A.M.M.A",
    )
    parser.add_argument('--anomaly', type=str, default=None, help="Path to ANOMALY directory")
    parser.add_argument('--gamma', type=str, default=None, help="Path to GAMMA directory")

    args = parser.parse_args()
    FullInstall().run(args)
