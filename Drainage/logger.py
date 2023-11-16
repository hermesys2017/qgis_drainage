import logging
import os
from datetime import datetime


def init_logger() -> None:
    logger = logging.getLogger("drainage")
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '{"logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s", "asctime": "%(asctime)s"}'
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    path = os.path.join(os.path.dirname(__file__), "log")
    os.makedirs(path, exist_ok=True)
    file_handler = logging.FileHandler(
        os.path.join(
            path,
            f"{datetime.now().strftime('%Y%m%d_%H%M%S_start')}.log",
        ),
        mode="a",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    error_file_handler = logging.FileHandler(
        os.path.join(
            path,
            f"{datetime.now().strftime('%Y%m%d_%H%M%S_error')}.log",
        ),
        mode="a",
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)


def get_logger() -> logging.Logger:
    return logging.getLogger("drainage")


def unload_logger() -> None:
    logger = logging.getLogger("drainage")
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
