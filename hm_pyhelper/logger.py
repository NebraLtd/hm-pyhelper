import os
import logging

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG")
_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s -- %(pathname)s:(%(lineno)d) - %(message)s"  # noqa: F541 E501


def get_stream_handler(log_format=_log_format):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOGLEVEL)
    stream_handler.setFormatter(logging.Formatter(log_format))
    return stream_handler


def get_logger(name, log_format=_log_format):
    logger = logging.getLogger(name)
    logger.setLevel(LOGLEVEL)
    logger.addHandler(get_stream_handler(log_format))
    return logger


def log(class_name):
    return get_logger(class_name)
