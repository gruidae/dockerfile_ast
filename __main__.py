import argparse
import logging
import sys

from dockerfile import GoIOError, GoParseError

from dockerfile_ast import DockerfileAST, DockerfileASTVisitor, DockerfileParser
import dockerfile_ast.util

_TEST_RAW_CODE = """FROM ubuntu
ONBUILD RUN set -eux \\
  && apt-get update \\
  && apt-get install -y --no-install-recommends httpd \\
  && rm -rf /var/lib/apt/lists/*
EXPOSE 80
ENTRYPOINT ["httpd"]
"""


def _init_argument_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Dockerfile AST Parser")
    parser.add_argument("filename", help="Dockerfile name you would like to parse")
    parser.add_argument("-o", "--output", help="Filename of DockerfileAST", metavar="filename")
    parser.add_argument("--exclude-label-instructions", help="", action="store_true")
    parser.add_argument(
        "--parse-level", help="Parse level (1: Dockerfile Instruction, 2: Shell Script, 3: Shell Command)",
        default=1, choices=[1, 2, 3], type=int
    )
    parser.add_argument("--separate-instructions", help="", action="store_true")
    parser.add_argument("--separate_run_instructions", help="", action="store_true")
    return parser


if __name__ == "__main__":
    argument_parser: argparse.ArgumentParser = _init_argument_parser()
    # parse command line arguments
    args: argparse.Namespace = argument_parser.parse_args()
    filename: str = args.filename
    exclude_label_instructions: bool = args.exclude_label_instructions
    parse_level: int = args.parse_level
    separate_instructions: bool = args.separate_instructions
    separate_run_instructions: bool = args.separate_run_instructions

    logger: logging.Logger = dockerfile_ast.util.init_logger(
        logging.DEBUG, "var/log/" + filename.replace("/", ".") + ".log", logging.WARNING
    )
    try:
        # parse Dockerfile
        logger.info("Parse " + filename)
        dfile_parser: DockerfileParser = DockerfileParser(
            exclude_label_instructions, parse_level, separate_instructions, separate_run_instructions, logger
        )
        dfile_ast: DockerfileAST = dfile_parser.parse_file(filename)
        visitor: DockerfileASTVisitor = DockerfileASTVisitor(dfile_ast, logger)
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
