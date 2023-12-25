import os

import lanutils
import tomlkit
from fastapi import FastAPI
from pathier import Pathier

from homecloud.homecloud_logging import get_logger

"$router_imports"

root = Pathier(__file__).parent
config = (root / "homecloud_config.toml").loads()

app = FastAPI()
"$router_includes"


def get_port_range() -> tuple[int, int]:
    """Get port_range from 'homecloud_config.toml'.
    Need to do all this casting because tomlkit class types
    mess things up."""
    port_range = tuple(config["port_range"])
    return (int(port_range[0]), int(port_range[1]))


def get_serving_address() -> tuple[str, int]:
    print("Obtaining ip address...")
    ip = lanutils.get_my_ip()[0][0]
    print("Finding available port in range...")
    port = lanutils.get_available_port(ip, get_port_range())
    return (ip, port)


def start_server(uvicorn_args: list[str] = ["--reload"]):
    logger = get_logger("$app_name_server")
    ip, port = get_serving_address()
    logger.info(f"Server started: http://{ip}:{port}")
    os.system(
        f"uvicorn {Pathier(__file__).stem}:app {' '.join(uvicorn_args)} --host {ip} --port {port}"
    )


if __name__ == "__main__":
    start_server(config["uvicorn_args"])
