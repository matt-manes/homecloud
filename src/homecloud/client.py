import json
import socket
import time

import requests
from pathier import Pathier

from homecloud import homecloud_logging, homecloud_utils


def on_fail(func):
    """If contacting the server fails,
    keep scanning for the server and retrying
    the request."""

    def inner(self, *args, **kwargs):
        counter = 0
        while True:
            try:
                output = func(self, *args, **kwargs)
                break
            except Exception as e:
                print("Error contacting server")
                print(e)
                print(f"Retrying in {counter}s")
                time.sleep(counter)
                if counter < 60:
                    counter += 1
                # After three consecutive fails,
                # start scanning for the server running
                # on a different ip and/or port
                if counter > 2:
                    self.server_url = self.wheres_my_server()
        return output

    return inner


class HomeCloudClient:
    def __init__(
        self,
        app_name: str,
        send_logs: bool = True,
        log_send_thresh: int = 10,
        log_level: str = "INFO",
        log_path: Pathier | str = None,
        timeout: int = 10,
    ):
        """Initialize client object.

        :param app_name: The app name to use.

        :param send_logs: Whether to send logs to the server
        in addition to local logging.

        :param log_send_thresh: The number of logging events required
        before sending logs to the server and flushing the current stream.

        :param log_level: The level of events to log.

        :param timeout: Number of seconds to wait for a response
        when sending a request."""
        self.app_name = app_name
        self.host_name = socket.gethostname()
        self.send_logs = send_logs
        self.log_send_thresh = log_send_thresh
        self.timeout = timeout
        if send_logs:
            self.logger, self.log_stream = homecloud_logging.get_client_logger(
                f"{self.app_name}_client", self.host_name, log_level, log_path
            )
        else:
            self.logger = homecloud_logging.get_logger(
                f"{self.app_name}_client", log_level, log_path
            )
        self.server_url = self.check_last_server()
        if not self.server_url:
            self.server_url = self.wheres_my_server()
        self.base_payload = self.get_base_payload()

    def wheres_my_server(self) -> str:
        """Returns the server url for this app.
        Raises an exception if it can't be found."""
        try:
            message = f"Searching for {self.app_name} server."
            print(message)
            self.logger.info(message)
            server_ip, server_port = homecloud_utils.get_homecloud_servers()[
                self.app_name
            ]
            message = f"Found {self.app_name} server at {server_ip}:{server_port}"
            print(message)
            self.logger.info(message)
            self.save_server(server_ip, server_port)
        except Exception as e:
            server_ip = ""
            server_port = ""
            message = f"Failed to find {self.app_name} server."
            print(message)
            self.logger.exception(message)
        return f"http://{server_ip}:{server_port}"

    def save_server(self, ip: str, port: int):
        """Save server ip and port to homecloud_config.toml
        as 'last_server_ip' and 'last_server_port' fields."""
        config = homecloud_utils.load_config()
        config["last_server_ip"] = ip
        config["last_server_port"] = port
        homecloud_utils.save_config(config)
        self.logger.info(
            f"Saved '{ip}' and '{port}' to 'last_server_ip' and 'last_server_port' fields in 'homecloud_config.toml'."
        )

    def check_last_server(self) -> str | None:
        """Load ./homecloud_config.toml
        and see if the last known homecloud server
        for this app is active at the address.
        If it is, return the server's url.
        If not, return None."""
        self.logger.info(
            f"Checking if 'homecloud_config.toml' contains previous server information."
        )
        config = homecloud_utils.load_config()
        if not config:
            self.logger.info(f"No 'homecloud_config.toml' found.")
            return None
        if "last_server_ip" in config and "last_server_port" in config:
            ip = config["last_server_ip"]
            port = config["last_server_port"]
            self.logger.info(
                f"Checking previously contacted server at http://{ip}:{port}"
            )
        else:
            self.logger.info(f"No previous server information found.")
            return None
        if homecloud_utils.is_homecloud_server(ip, port) == self.app_name:
            self.logger.info(f"Previous server at http://{ip}:{port} is active.")
            return f"http://{ip}:{port}"
        else:
            self.logger.info(f"Previous server at http://{ip}:{port} is not active.")
            return None

    def get_base_payload(self) -> dict:
        """Can be overridden without having to override self.__init__()"""
        return {"host": self.host_name}

    def send_request(
        self, method: str, resource: str, data: dict = {}, params: dict = {}
    ) -> requests.Response:
        """Send a request to the server.

        :param method: The method to use (get, post, etc.).

        :param resource: The path location of the requested resource
        (e.g. /users/me).

        :param data: The request body.

        :param params: Url parameters."""
        # Push logs if applicable
        if self.send_logs and (
            len(self.log_stream.getvalue().splitlines()) >= self.log_send_thresh
        ):
            self.push_logs()
        data |= self.base_payload
        url = f"{self.server_url}{resource}"
        data = json.dumps(data)
        return requests.request(
            method, url, data=data, params=params, timeout=self.timeout
        )

    def push_logs(self):
        """Push log stream to the server."""
        self.logger.info(f"Pushing log stream to {self.app_name} server.")
        log_stream = self.log_stream.getvalue()
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        self.send_request("post", "/clientlogs", data={"log_stream": log_stream})
