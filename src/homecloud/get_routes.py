from pathlib import Path

import request_models
from fastapi import APIRouter

from homecloud import homecloud_logging

root = Path(__file__).parent

router = APIRouter()
logger = homecloud_logging.get_logger("$app_name_server")


@router.get("/homecloud")
def homecloud(request: request_models.Request) -> dict:
    # You can add to the payload here if you want
    # but don't remove anything or the server will be
    # undiscoverable by homecloud clients.
    logger.info(f"{request.host} says hello")
    return {"app_name": "$app_name", "host": request.host}
