from typing import List

from dockerfile_ast.dockerfile_items.nodes import Instruction


class DockerfileAST:
    __REPR_FORMAT: str = "{0}(instructions={0}, raw_code={1})"

    def __init__(self, instructions: List[Instruction], raw_code: str):
        self.__instructions = instructions
        self.__raw_code = raw_code

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_instructions = repr(self.__instructions)
        repr_raw_code = repr(self.__raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_instructions, repr_raw_code)

    @property
    def instructions(self) -> List[Instruction]:
        return [instruction for instruction in self.__instructions]

    @property
    def raw_code(self) -> str:
        return self.__raw_code


class DockerfileASTVisitor:
    def __init__(self, dockerfile_ast: DockerfileAST):
        self.__ast = dockerfile_ast

    def visit(self) -> bool:
        for instruction in self.__ast.instructions:
            can_visit = self.__visit_instruction(instruction)
            if not can_visit:
                return can_visit
        return can_visit

    def __visit_instruction(self, instruction: Instruction) -> bool:
        print(instruction)
        return True
