from typing import List

import dockerfile


class Instruction:
    __REPR_FORMAT: str = "{0}(line_num={1}, raw_code={2})"

    def __init__(self, line_num: int, raw_code: str):
        self.__line_num: int = line_num
        self.__raw_code: str = raw_code

    @property
    def raw_code(self):
        return self.__raw_code

    def __str__(self):
        return self.__raw_code

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_line_num = repr(self.__line_num)
        repr_raw_code = repr(self.__raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_line_num, repr_raw_code)


class FROMInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class RUNInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class CMDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class LABELInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class EXPOSEInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class ENVInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class ADDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class COPYInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class ENTRYPOINTInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class VOLUMEInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class USERInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class WORKDIRInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class ARGInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class ONBUILDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class STOPSIGNALInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class HEALTHCHECKInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)


class SHELLInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)
