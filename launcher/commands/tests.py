from launcher.common import gamma_arg


class TestModMaker:

    arguments: dict = {
        **gamma_arg,
    }

    name: str = "test-mod-maker"

    help: str = "Testing mod maker directives"

    def run(self, args) -> None:
        raise NotImplementedError("TestModMaker is disabled for now following `launcher.mods` modification")
