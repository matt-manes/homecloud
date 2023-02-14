import tomlkit
import os
from pathlib import Path
from fastapi import FastAPI
import server_config
import json
import request_models
import lanutils
import homecloud_utils

root = Path(__file__).parent

app = FastAPI()
""" router_includes """


@app.get("/homecloud")
def ping(request: request_models.Request):
    # You can add to the payload here if you want
    # but don't remove anything or the server will be
    # undiscoverable by homecloud clients.
    return {"app_name": "$app_name", "host": request.host}


def get_serving_address() -> tuple[str, int]:
    print("Obtaining ip address...")
    ip = lanutils.get_myip()[0][0]
    print("Finding available port in range...")
    port = lanutils.get_available_port(ip, homecloud_utils.get_port_range())
    return (ip, port)


def start_server(uvicorn_args: list[str] = ["--reload"]):
    ip, port = get_serving_address()
    os.system(
        f"uvicorn {Path(__file__).stem}:app {' '.join(uvicorn_args)} --host {ip} --port {port}"
    )


if __name__ == "__main__":
    start_server()
