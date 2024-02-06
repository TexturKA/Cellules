import logging
from .file_manager import FileManager

log_fm = FileManager("logs", "log")


def getLogger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    log_fm.write([])
    handler = logging.FileHandler(log_fm.path)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
