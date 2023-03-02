import logging
from pathlib import Path
import socket
from io import StringIO
import inspect

root = Path(__file__).parent


def get_logger(log_name: str, log_level: str = "INFO") -> logging.Logger:
    """Get a homecloud logger.
    All logs will be written to a "logs" sub directory of this file's
    parent directory.

    :param log_name: The name of the log, e.g. 'myapp_server' or 'myapp_client'.

    :param log_level: The level for this logger to log at. Same specifications
    as the build in logging module."""
    logger = logging.getLogger(log_name)

    if not logger.hasHandlers():
        root = Path(inspect.stack()[-1].filename).parent
        (root / "logs").mkdir(exist_ok=True, parents=True)
        handler = logging.FileHandler(str(root / "logs" / f"{log_name}.log"))
        handler.setFormatter(
            logging.Formatter(
                "{levelname}|-|{asctime}|-|{message}",
                style="{",
                datefmt="%m/%d/%Y %I:%M:%S %p",
            )
        )
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)
    return logger


def get_client_logger(
    log_name: str, host: str, log_level: str = "INFO"
) -> tuple[logging.Logger, StringIO]:
    logger = get_logger(log_name, log_level)
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
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger = logging.LoggerAdapter(logger, {"host": host})
    return logger, log_stream
