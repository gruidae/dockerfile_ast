import logging
import sys

from dockerfile import GoIOError, GoParseError

from dockerfile_ast import DockerfileAST, DockerfileASTVisitor, DockerfileParser


def _init_logger() -> logging.Logger:
    logging_logger = logging.getLogger(__name__)
    # ログで出力するレベルを指定
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.WARNING)
    # ログのフォーマットを指定
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    stream_handler.setFormatter(formatter)
    logging_logger.addHandler(stream_handler)
    return logging_logger


def _parse_file(filename: str, logging_logger: logging.Logger) -> DockerfileAST:
    dfile_ast = None
    try:
        dockerfile_parser = DockerfileParser()
        dfile_ast = dockerfile_parser.parse_file(filename)
    except GoParseError as e:
        if hasattr(e, "message"):
            logging_logger.error(e.message)
        else:
            logging_logger.error(e)
    except GoIOError as e:
        if hasattr(e, "message"):
            logging_logger.error(e.message)
        else:
            logging_logger.error(e)
    except IOError as e:
        if hasattr(e, "message"):
            logging_logger.error(e.message)
        else:
            logging_logger.error(e)
    except ValueError as e:
        if hasattr(e, "message"):
            logging_logger.error(e.message)
        else:
            logging_logger.error(e)
    return dfile_ast


if __name__ == "__main__":
    filename = sys.argv[1]
    logger: logging.Logger = _init_logger()
    dfile_ast = _parse_file(filename, logger)
    visitor: DockerfileASTVisitor = DockerfileASTVisitor(dfile_ast)
    visitor.visit()
