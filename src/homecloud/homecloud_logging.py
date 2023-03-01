import logging
from pathlib import Path
import socket
from io import StringIO

root = Path(__file__).parent


def get_logger(logname: str, loglevel: str = "INFO") -> logging.Logger:
    """Get a homecloud logger.
    All logs will be written to a "logs" sub directory of this file's
    parent directory.

    :param logname: The name of the log, e.g. 'myapp_server' or 'myapp_client'.

    :param loglevel: The level for this logger to log at. Same specifications
    as the build in logging module."""
    logger = logging.getLogger(logname)

    if not logger.hasHandlers():
        (root / "logs").mkdir(exist_ok=True, parents=True)
        handler = logging.FileHandler(str(root / "logs" / f"{logname}.log"))
        handler.setFormatter(
            logging.Formatter(
                "{levelname}|-|{asctime}|-|{message}",
                style="{",
                datefmt="%m/%d/%Y %I:%M:%S %p",
            )
        )
        handler.setLevel(loglevel)
        logger.addHandler(handler)
        logger.setLevel(loglevel)
    return logger


def get_client_logger(
    logname: str, host: str, loglevel: str = "INFO"
) -> tuple[logging.Logger, StringIO]:
    logger = get_logger(logname, loglevel)
    if all(logging.StreamHandler != type(handler) for handler in logger.handlers):
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(
            logging.Formatter(
                "{levelname}|-|{host}|-|{asctime}|-|{message}",
                style="{",
                datefmt="%m/%d/%Y %I:%M:%S %p",
            )
        )
        handler.setLevel(loglevel)
        logger.addHandler(handler)
        logger.setLevel(loglevel)
        logger = logging.LoggerAdapter(logger, {"host": host})
    return logger, log_stream
