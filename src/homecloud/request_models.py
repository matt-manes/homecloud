from typing import Optional
from pydantic import BaseModel
from typing import Any


class Request(BaseModel):
    host: str
