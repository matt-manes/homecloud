from pathlib import Path

from fastapi import APIRouter
from homecloud import homecloud_logging

import request_models

root = Path(__file__).parent

router = APIRouter()
logger = homecloud_logging.get_logger("$app_name_server")
