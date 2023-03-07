from typing import Any, Optional

from pydantic import BaseModel


class Request(BaseModel):
    host: str


class LogsRequest(Request):
    log_stream: str
