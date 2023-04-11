from pathier import Pathier

from homecloud import homecloud_generator, homecloud_utils
import sys

root = Pathier(__file__).parent


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
    dummy_path.mkcwd()
    assert homecloud_utils.load_config()
    config = homecloud_utils.load_config()
    assert all(item in config for item in ["port_range", "uvicorn_args"])
    root.mkcwd()
    # dummy_path.delete()
    input("start dummy_server.py before continuing...")


def test__push_logs():
    (root / "dummy").mkcwd()
    sys.path.insert(0, str(root / "dummy"))
    import dummy_client

    client = dummy_client.DummyClient(log_send_thresh=2, log_level="DEBUG")
    for _ in range(10):
        client.hello()
