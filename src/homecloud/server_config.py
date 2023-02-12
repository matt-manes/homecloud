import ifaddr
import socket
from pathlib import Path
import tomlkit

root = Path(__file__).parent

import argparse


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "adapter_type",
        default="Ethernet",
        nargs="?",
        type=str,
        help=""" The adapter type to try to find device's ip address for.
        Should be 'Ethernet' or 'Wi-Fi'.""",
    )

    parser.add_argument(
        "-op",
        "--overwrite_port",
        action="store_true",
        help=""" Whether to overwrite the current config's port with
        a new random available port.""",
    )

    parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        default=None,
        help=""" The path to store 'server_config.toml' in.
        If not provided, the current working directory will be used.""",
    )

    args = parser.parse_args()
    if not args.output_path:
        args.output_path = Path.cwd()

    return args


def get_ip_options() -> list[tuple[str, str]]:
    """Returns a list of tuples.
    Each inner tuple is an IPv4 address
    and the adapter name.
    Only looks for "Ethernet" and "Wi-Fi"
    addresses not in the '169.254' block."""
    return [
        (ip.ip, ip.nice_name)
        for adapter in ifaddr.get_adapters()
        for ip in adapter.ips
        if ip.nice_name in ["Ethernet", "Wi-Fi"]
        and ip.ip.count(".") == 3
        and ":" not in ip.ip
        and not ip.ip.startswith("169.254.")
    ]


def get_available_port() -> str:
    """Returns a port number that is currently unused."""
    with socket.socket() as sock:
        sock.bind(("", 0))
        return sock.getsockname()[1]


def write_config(ip: str, port: int, config_dir: Path | str = None):
    """Writes ip and port to 'server_config.toml'.

    :param ip: The IPv4 address to use.

    :param port: The port to use.

    :param config_dir: The directory to write
    'server_config.toml' into.
    If None, it will be written to the directory
    containing this file."""
    config_path = (
        Path(config_dir) / "server_config.toml"
        if config_dir
        else root / "server_config.toml"
    )
    config_path.write_text(tomlkit.dumps({"ip": ip, "port": port}))


def configure_server(
    adapter_type: str, overwrite_port: bool = False, config_dir: Path | str = None
) -> bool:
    """Try to determine appropriate host ip address
    and an available port, then write it to 'server_config.toml'.

    :param adapter_type: Sould be one of 'Ethernet' or 'Wi-Fi'.

    :param overwrite_port: Whether to overwrite the existing
    port number in 'server_config.toml', if there is one.

    :param config_dir: The directory to write
    'server_config.toml' into.
    If None, it will be written to the directory
    containing this file.

    :return bool: Returns whether configuration was successful."""

    config_path = (
        Path(config_dir) / "server_config.toml"
        if config_dir
        else root / "server_config.toml"
    )
    config = {}
    if not config_path.exists():
        overwrite_port = True
    else:
        config = tomlkit.loads(config_path.read_text())
        if "port" not in config:
            overwrite_port = True

    ip_options = get_ip_options()
    names = [option[1] for option in ip_options]
    if len(ip_options) == 1:
        print(f"Only one adapter '{ip_options[0][1]}' found.")
        print(f"Using its address: '{ip_options[0][0]}'.")
        ip = ip_options[0][0]
    elif adapter_type.lower() not in [option[1].lower() for option in ip_options]:
        print(f"Could not find ip address for adapter '{adapter_type}'.")
        names = "', '".join([option[1] for option in ip_options])
        print(f"Only found: '{names}'.")
        return False
    else:
        ip = [
            option[0]
            for option in ip_options
            if adapter_type.lower() == option[1].lower()
        ][0]
    config["ip"] = ip
    if overwrite_port:
        config["port"] = get_available_port()
    config_path.write_text(tomlkit.dumps(config))
    return True


def main(args: argparse.Namespace):
    configure_server(args.adapter_type, args.overwrite_port, args.output_path)


if __name__ == "__main__":
    main(get_args())
