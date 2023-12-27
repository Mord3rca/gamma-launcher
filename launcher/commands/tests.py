class TestModMaker:

    arguments: dict = {
        "--gamma": {
            "help": "Path to GAMMA directory",
            "required": True,
            "type": str
        },
    }

    name: str = "test-mod-maker"

    help: str = "Testing mod maker directives"

    def run(self, args) -> None:
        raise NotImplementedError("TestModMaker is disabled for now following `launcher.mods` modification")
