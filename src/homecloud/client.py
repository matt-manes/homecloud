import json
import socket
import time
from typing import Any

import requests

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
                print(str(e))
                print(f"Retrying in {counter}s")
                time.sleep(counter)
                if counter < 60:
                    counter += 1
                # After three consecutive fails,
                # start scanning for the server running
                # on a different ip and/or port
                if counter > 2:
                    self.server_url = self.wheres_my_server()
        if self.send_logs and (
            len(self.log_stream.getvalue().splitlines()) >= self.log_send_thresh
        ):
            self.push_logs()
        return output

    return inner


class HomeCloudClient:
    def __init__(
        self,
        app_name: str,
        send_logs: bool = True,
        log_send_thresh: int = 10,
        log_level: str = "INFO",
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
                f"{self.app_name}_client", self.host_name, log_level
            )
        else:
            self.logger = homecloud_logging.get_logger(
                f"{self.app_name}_client", log_level
            )
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
        except Exception as e:
            server_ip = ""
            server_port = ""
            message = f"Failed to find {self.app_name} server."
            print(message)
            self.logger.exception(message)
        return f"http://{server_ip}:{server_port}"

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
        data |= self.base_payload
        url = f"{self.server_url}{resource}"
        data = json.dumps(data)
        return requests.request(
            method, url, data=data, params=params, timeout=self.timeout
        )

    def push_logs(self):
        """Push log stream to the server."""
        self.logger.info(f"Pushing log stream to {self.app_name} server.")
        self.send_request(
            "post", "/clientlogs", data={"log_stream": self.log_stream.getvalue()}
        )
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
