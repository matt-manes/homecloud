from fastapi import APIRouter
from homecloud import request_models
from homecloud import homecloud_logging

router = APIRouter()
logger = homecloud_logging.get_logger("$app_name_server")
