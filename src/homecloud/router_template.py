import request_models
from fastapi import APIRouter
from pathier import Pathier

from homecloud import homecloud_logging

root = Pathier(__file__).parent

router = APIRouter()
logger = homecloud_logging.get_logger("$app_name_server")
