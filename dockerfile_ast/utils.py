from abc import ABCMeta
import logging
import sys


class DockerfileASTNode(metaclass=ABCMeta):
    """
    A node of all possible syntax for Dockerfile AST.
    """
    __REPR_FORMAT: str = "{0}()"

    def __repr__(self):
        self_class_name = self.__class__.__name__
        return self.__REPR_FORMAT.format(self_class_name)

    def __str__(self):
        self_class_name = self.__class__.__name__
        return self.__REPR_FORMAT.format(self_class_name)



def init_logger(stream_level: int, log_filename: str, file_level: int) -> logging.Logger:
    """
    Initialize ``logging.Logger`` for Dockerfile AST.

    Parameters
    ----------
    stream_level : int
        Logging level of StreamHandler.
    log_filename : str
        Log file name.
    file_level : int
        Logging level of FileHandler.

    Returns
    -------
    logging_logger : logging.Logger
        logging.Logger for Dockerfile AST.
    """
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
