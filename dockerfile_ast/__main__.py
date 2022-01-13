import logging
import sys

from dockerfile import GoIOError, GoParseError

from dockerfile_ast import DockerfileAST, DockerfileASTVisitor, DockerfileParser


def _init_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    # ログで出力するレベルを指定
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.WARNING)
    # ログのフォーマットを指定
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def _parse_file(filename: str, logger: logging.Logger) -> DockerfileAST:
    dockerfile_parser = DockerfileParser()
    dfile_ast: DockerfileAST = None
    try:
        dfile_ast = dockerfile_parser.parse_file(filename)
    except GoParseError as e:
        if hasattr(e, "message"):
            logger.error(e.message)
        else:
            logger.error(e)
    except GoIOError as e:
        if hasattr(e, "message"):
            logger.error(e.message)
        else:
            logger.error(e)
    except IOError as e:
        if hasattr(e, "message"):
            logger.error(e.message)
        else:
            logger.error(e)
    return dfile_ast


if __name__ == "__main__":
    filename = sys.argv[1]
    logger: logging.Logger = _init_logger()
    dfile_ast = _parse_file(filename, logger)
    visitor: DockerfileASTVisitor = DockerfileASTVisitor(dfile_ast)
    visitor.visit()
