from homecloud import homecloud_generator
from pathlib import Path

root = Path(__file__).parent


class MockArgs:
    def __init__(self):
        self.app_name = "dummy"
        self.routes = ["put"]
        self.destination = root / "dummy"


def test__main():
    args = MockArgs()
    homecloud_generator.main(args)
    dummy_path = root / "dummy"

    def assert_(name: str):
        assert (dummy_path / f"dummy_{name}").exists()

    for file in [
        "get_routes.py",
        "post_routes.py",
        "put_routes.py",
        "server.py",
        "request_models.py",
        "client.py",
    ]:
        assert_(file)
    assert (dummy_path / "homecloud_config.toml").exists()
