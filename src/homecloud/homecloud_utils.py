import ifaddr
import socket
import ipaddress
import requests
from concurrent.futures import ThreadPoolExecutor
import icmplib
import tomlkit
from pathlib import Path
import json
import lanutils

root = Path(__file__).parent


def get_port_range() -> tuple[int, int]:
    """Get port_range from 'homecloud_config.toml'.
    Need to do all this casting because tomlkit class types
    mess things up."""
    port_range = tuple(
        tomlkit.loads((root / "homecloud_config.toml").read_text())["port_range"]
    )
    return (int(port_range[0]), int(port_range[1]))


def is_homecloud_server(ip: str, port: int) -> str | bool:
    """Determine if ip address and port number
    are active as a homecloud server.
    The 'homecloud' route of a homecloud server should return
    the app name the server is serving and the host
    name of the device that made the request.

    Returns the app name of the server if it
    is a homecloud server, else return False."""
    url = f"http://{ip}:{port}/homecloud"
    host = socket.gethostname()
    try:
        response = json.loads(
            requests.get(url, data=json.dumps({"host": host}), timeout=1).text
        )
        if response["host"] == host:
            return response["app_name"]
        else:
            return False
    except Exception as e:
        return False


def get_homecloud_servers() -> dict[str, tuple[str, int]]:
    """Scan the local network for servers.

    Returns a dictionary where the key is the app name
    and the value is a tuple containing the ip address
    and the port number serving that app.
    >>> print(get_homecloud_servers())
    >>> {"$app_name": ("10.0.0.49", 50025), "$app_name2": ("10.0.0.32", 50041)}"""
    ips = lanutils.enumerate_devices()
    port_range = get_port_range()
    # Get all open ports in port_range for all ips
    with ThreadPoolExecutor() as executor:
        threads = [executor.submit(lanutils.scan_ports, ip, port_range) for ip in ips]
    open_addresses = [
        (ip, port)
        for ip, thread in zip(ips, threads)
        for port in thread.result()
        if len(thread.result()) > 0
    ]
    # Scan ports of ips for homecloud servers
    with ThreadPoolExecutor() as executor:
        threads = [
            executor.submit(
                is_homecloud_server,
                address[0],
                address[1],
            )
            for address in open_addresses
        ]
    return {
        thread.result(): (address[0], address[1])
        for address, thread in zip(open_addresses, threads)
        if thread.result()
    }
