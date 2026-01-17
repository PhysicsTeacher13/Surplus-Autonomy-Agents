from pathlib import Path

class FixtureStore:
    """
    Simple fixture loader for deterministic tests.

    Use when run_config["network"] == "OFF".
    """
    def __init__(self, root: str):
        self.root = Path(root)

    def path(self, relative: str) -> Path:
        p = self.root / relative
        if not p.exists():
            raise FileNotFoundError(f"Fixture not found: {p}")
        return p

    def read_text(self, relative: str, encoding: str = "utf-8") -> str:
        return self.path(relative).read_text(encoding=encoding)

    def read_bytes(self, relative: str) -> bytes:
        return self.path(relative).read_bytes()
