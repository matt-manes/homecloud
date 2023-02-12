import json
import time
import socket
import requests
from typing import Any
import homecloud_utils


class HomeCloudClient:
    def __init__(self):
        self.app_name = "$app_name"
        self.server_url = self.wheres_my_server()
        self.host_name = socket.gethostname()
        self.base_payload = self.get_base_payload()

    def _on_fail(func):
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
            return output

        return inner

    def wheres_my_server(self) -> str:
        """Returns the server url for this app.
        Raises an exception if it can't be found."""
        try:
            server_ip, server_port = homecloud_utils.get_homecloud_servers()[
                self.app_name
            ]
        except Exception as e:
            server_ip = ""
            server_port = ""
        return f"http://{server_ip}:{server_port}"

    def get_base_payload(self) -> dict:
        """Can be overridden without having to override self.__init__()"""
        return {"host": self.host_name}

    def send_request(
        self, method: str, resource: str, data: dict = {}
    ) -> requests.Response:
        data |= self.base_payload
        url = f"{self.server_url}/{resource}"
        data = json.dumps(data)
        return requests.request(method, url, data=data)

    @_on_fail
    def hello(self) -> str:
        """Contacts the server and returns the app name."""
        return json.loads(self.send_request("get", "homecloud").text)["app_name"]
