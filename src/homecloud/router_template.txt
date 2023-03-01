from fastapi import APIRouter
import request_models
import homecloud_logging

router = APIRouter()
logger = homecloud_logging.get_logger("$app_name_server")