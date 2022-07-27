import logging
from typing import List

import dockerfile_ast.util
from dockerfile_ast.dockerfile_items.nodes import Instruction


class DockerfileAST:
    """
    An AST (Abstract Syntax Tree) of Dockerfile.

    You need to use `dockerfile_ast.DockerfileASTVisitor`
    when you would like to visit syntax nodes in this `DockerfileAST` class.

    Attributes
    ----------
    __instructions: List[Instruction]
        List of Dockerfile Instructions
    __raw_code: str
        Original Dockerfile source code.
    """
    __REPR_FORMAT: str = "{0}(instructions={0}, raw_code={1})"

    def __init__(self, instructions: List[Instruction], raw_code: str):
        """
        An AST (Abstract Syntax Tree) of Dockerfile.

        Parameters
        ----------
        instructions : List[Instruction]
            List of Dockerfile Instructions
        raw_code : str
            Original Dockerfile source code.
        """
        self.__instructions = instructions
        self.__raw_code = raw_code

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_instructions = repr(self.__instructions)
        repr_raw_code = repr(self.__raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_instructions, repr_raw_code)

    @property
    def instructions(self) -> List[Instruction]:
        """
        Returns
        -------
        __instructions : List[Instruction]
            List of Dockerfile Instructions.
        """
        return self.__instructions

    @property
    def raw_code(self) -> str:
        """
        Returns
        -------
        __raw_code : str
            Original Dockerfile source code.
        """
        return self.__raw_code


class DockerfileASTVisitor:
    """
    A visitor in order to visit each node in Dockerfile AST.
    """
    def __init__(self, ast: DockerfileAST, logger: logging.Logger = None):
        """
        A visitor in order to visit each node in Dockerfile AST.

        Parameters
        ----------
        ast : DockerfileAST
            Dockerfile AST.
        logger : logging.Logger
            Logger in order to log debug, warning or error messages.
        """
        self.__ast = ast
        if logger is None:
            self.__logger = dockerfile_ast.util.init_logger(logging.WARNING, None, logging.WARNING)
        else:
            self.__logger = logger

    def visit(self) -> bool:
        for instruction in self.__ast.instructions:
            can_visit = self.__visit_instruction(instruction)
            if not can_visit:
                return False
        return True

    def __visit_instruction(self, instruction: Instruction) -> bool:
        self.__logger.info(repr(instruction))
        return True
