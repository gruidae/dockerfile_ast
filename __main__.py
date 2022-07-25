import argparse
import logging
import sys

from dockerfile import GoIOError, GoParseError

from dockerfile_ast import BashParser, DockerfileAST, DockerfileASTVisitor, DockerfileParser


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


def _init_argument_parser() -> argparse.ArgumentParser:
    argparse_argument_parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Dockerfile AST Parser")
    argparse_argument_parser.add_argument("filename", help="Dockerfile name you would like to parse")
    argparse_argument_parser.add_argument("-o", "--output", help="Filename of DockerfileAST", metavar="filename")
    argparse_argument_parser.add_argument("--exclude-label-instructions", help="", action="store_true")
    argparse_argument_parser.add_argument(
        "--parse-level", help="Parse level (1: Dockerfile Instruction, 2: Shell Script, 3: Shell Command)",
        default=1, choices=[1, 2, 3], type=int
    )
    argparse_argument_parser.add_argument("--separate-instructions", help="", action="store_true")
    argparse_argument_parser.add_argument("--separate_run_instructions", help="", action="store_true")
    return argparse_argument_parser


def _parse(
        raw_code: str,
        exclude_label_instructions: bool,
        parse_level: int,
        separate_instructions: bool,
        separate_run_instructions: bool
) -> DockerfileAST:
    dockerfile_parser = DockerfileParser(
        exclude_label_instructions, parse_level, separate_instructions, separate_run_instructions
    )
    return dockerfile_parser.parse(raw_code)


def _parse_file(
        filename: str,
        exclude_label_instructions: bool,
        parse_level: int,
        separate_instructions: bool,
        separate_run_instructions: bool
) -> DockerfileAST:
    dockerfile_parser = DockerfileParser(
        exclude_label_instructions, parse_level, separate_instructions, separate_run_instructions
    )
    return dockerfile_parser.parse_file(filename)


if __name__ == "__main__":
    logger: logging.Logger = _init_logger()
    argument_parser: argparse.ArgumentParser = _init_argument_parser()

    try:
        # parse command line arguments
        args: argparse.Namespace = argument_parser.parse_args()
        filename = args.filename
        exclude_label_instructions = args.exclude_label_instructions
        parse_level = args.parse_level
        separate_instructions = args.separate_instructions
        separate_run_instructions = args.separate_run_instructions

        # parse Dockerfile
        # dfile_ast: DockerfileAST = _parse(_TEST_RAW_CODE, , exclude_label_instructions, parse_level, separate_instructions, separate_run_instructions)
        dfile_ast: DockerfileAST = _parse_file(filename, exclude_label_instructions, parse_level, separate_instructions, separate_run_instructions)
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
