from pathlib import Path
import os
from homecloud import homecloud_generator, homecloud_utils

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
    os.chdir(str(dummy_path))
    assert homecloud_utils.load_config()
    config = homecloud_utils.load_config()
    assert all(item in config for item in ["port_range", "uvicorn_args"])
