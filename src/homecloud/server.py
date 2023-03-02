import os
from pathlib import Path
from fastapi import FastAPI
import lanutils
import homecloud_utils
from homecloud_logging import get_logger
import tomlkit

"$router_imports"
import get_routes
import post_routes

root = Path(__file__).parent

app = FastAPI()
app.include_router(get_routes.router)
app.include_router(post_routes.router)
"$router_includes"


def get_port_range() -> tuple[int, int]:
    """Get port_range from 'homecloud_config.toml'.
    Need to do all this casting because tomlkit class types
    mess things up."""
    port_range = tuple(
        tomlkit.loads((root / "homecloud_config.toml").read_text())["port_range"]
    )
    return (int(port_range[0]), int(port_range[1]))


def get_serving_address() -> tuple[str, int]:
    print("Obtaining ip address...")
    ip = lanutils.get_myip()[0][0]
    print("Finding available port in range...")
    port = lanutils.get_available_port(ip, get_port_range())
    return (ip, port)


def start_server(uvicorn_args: list[str] = ["--reload"]):
    logger = get_logger("$app_name_server")
    ip, port = get_serving_address()
    logger.info(f"Server started: http://{ip}:{port}")
    os.system(
        f"uvicorn {Path(__file__).stem}:app {' '.join(uvicorn_args)} --host {ip} --port {port}"
    )


if __name__ == "__main__":
    start_server()
