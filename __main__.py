import logging
import sys

from dockerfile import GoIOError, GoParseError

from dockerfile_ast import DockerfileAST, DockerfileASTVisitor, DockerfileParser


_TEST_RAW_CODE = """FROM ubuntu
ONBUILD RUN set -eux \\
  && apt-get update \\
  && apt-get install -y --no-install-recommends httpd \\
  && rm -rf /var/lib/apt/lists/*
EXPOSE 80
ENTRYPOINT ["httpd"]
"""


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


def _parse(raw_code: str) -> DockerfileAST:
    dockerfile_parser = DockerfileParser()
    return dockerfile_parser.parse(raw_code)


def _parse_file(filename: str) -> DockerfileAST:
    dockerfile_parser = DockerfileParser()
    return dockerfile_parser.parse_file(filename)


if __name__ == "__main__":
    # filename = sys.argv[1]
    logger: logging.Logger = _init_logger()
    try:
        dfile_ast: DockerfileAST = _parse(_TEST_RAW_CODE)
        # dfile_ast: DockerfileAST = _parse_file(filename)
        visitor: DockerfileASTVisitor = DockerfileASTVisitor(dfile_ast)
        visitor.visit()
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
    except ValueError as e:
        if hasattr(e, "message"):
            logger.error(e.message)
        else:
            logger.error(e)
