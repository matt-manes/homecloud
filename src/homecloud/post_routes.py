from pathier import Pathier

import request_models
from fastapi import APIRouter

from homecloud import homecloud_logging

root = Pathier(__file__).parent

router = APIRouter()
logger = homecloud_logging.get_logger("$app_name_server")


@router.post("/clientlogs")
def writelogs(request: request_models.LogsRequest):
    with (root / "logs" / f"{request.host}.log").open("a") as logfile:
        logfile.write(request.log_stream)
