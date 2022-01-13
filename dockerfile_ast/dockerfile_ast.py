from typing import Tuple, List

import dockerfile

from dfile.nodes import Instruction


class DockerfileAST:
    def __init__(self, instructions: List[Instruction], raw_code: str):
        self.__instructions = instructions
        self.__raw_code = raw_code

    def __repr__(self):
        repr_format = "DockerfileAST(instructions={0},raw_code={1})"
        return repr_format.format(repr(self.__instructions), repr(self.__raw_code))

    @property
    def instructions(self):
        return [instruction for instruction in self.__instructions]

    @property
    def raw_code(self):
        return self.__raw_code

    @staticmethod
    def generate(cst: Tuple[dockerfile.Command], raw_code: str):
        instructions: List[Instruction] = list()
        for cst_instruction in cst:
            # print(cst_instruction)
            instructions.append(Instruction.generate(cst_instruction))
        return DockerfileAST(instructions, raw_code)


class DockerfileParser:
    def __init__(self, separate_instruction: bool = False):
        self.__filename = None
        self.__separate_instruction = separate_instruction

    @property
    def filename(self):
        return self.__filename

    def parse(self, raw_code: str) -> DockerfileAST:
        self.__filename = None
        cst: Tuple[dockerfile.Command] = dockerfile.parse_string(raw_code)
        return DockerfileAST.generate(cst, raw_code)

    def parse_file(self, filename: str) -> DockerfileAST:
        self.__filename = filename
        with open(filename) as fp:
            raw_code = fp.read()
        cst: Tuple[dockerfile.Command] = dockerfile.parse_file(filename)
        return DockerfileAST.generate(cst, raw_code)


class DockerfileASTVisitor:
    def __init__(self, dockerfile_ast: DockerfileAST):
        self.__ast = dockerfile_ast

    def visit(self) -> bool:
        can_visit: bool = False
        for instruction in self.__ast.instructions:
            can_visit = self.__visit_instruction(instruction)
            if not can_visit:
                return can_visit
        return can_visit

    def __visit_instruction(self, instruction: Instruction):
        print(instruction)
        return True
