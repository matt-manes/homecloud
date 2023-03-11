from pathlib import Path

import request_models
from fastapi import APIRouter

from homecloud import homecloud_logging

root = Path(__file__).parent

router = APIRouter()
logger = homecloud_logging.get_logger("$app_name_server")
