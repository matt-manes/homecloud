import json

import requests

from homecloud import HomeCloudClient, on_fail


class app_nameClient(HomeCloudClient):
    def __init__(
        self,
        app_name: str = "$app_name",
        send_logs: bool = True,
        log_send_thresh: int = 10,
        log_level: str = "INFO",
        timeout: int = 10,
    ):
        super().__init__(app_name, send_logs, log_send_thresh, log_level, timeout)

    @on_fail
    def hello(self) -> str:
        """Contacts the server and returns the app name."""
        self.logger.debug(f"Saying hello to the {self.app_name} server.")
        return json.loads(self.send_request("get", "/homecloud").text)["app_name"]
