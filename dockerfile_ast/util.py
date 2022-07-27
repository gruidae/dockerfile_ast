import logging
import sys


def init_logger(stream_level: int, log_filename: str, file_level: int) -> logging.Logger:
    logging_logger = logging.getLogger(__name__)
    # ログで出力するレベルを指定
    logging_logger.setLevel(logging.DEBUG)

    # StreamHandler
    stream_handler: logging.StreamHandler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(stream_level)
    stream_formatter: logging.Formatter = logging.Formatter("%(levelname)s: %(message)s")
    stream_handler.setFormatter(stream_formatter)
    logging_logger.addHandler(stream_handler)

    # FileHandler
    if log_filename is not None or len(log_filename) > 0:
        file_handler: logging.FileHandler = logging.FileHandler(log_filename)
        file_handler.setLevel(file_level)
        file_formatter: logging.Formatter = logging.Formatter("%(asctime)s - %(filename)s: %(levelname)s: %(message)s")
        file_handler.setFormatter(file_formatter)
        logging_logger.addHandler(file_handler)
    return logging_logger
