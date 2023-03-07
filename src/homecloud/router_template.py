from fastapi import APIRouter

from homecloud import homecloud_logging, request_models

router = APIRouter()
logger = homecloud_logging.get_logger("$app_name_server")
