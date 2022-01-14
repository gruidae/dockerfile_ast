from typing import List


class Instruction:
    __REPR_FORMAT: str = "{0}(line_num={1}, raw_code={2})"

    def __init__(self, line_num: int, raw_code: str):
        self.__line_num: int = line_num
        self.__raw_code: str = raw_code

    @property
    def line_num(self) -> int:
        return self.__line_num

    @property
    def raw_code(self) -> str:
        return self.__raw_code

    """
    def __str__(self):
        return self.__raw_code
    """

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_line_num = repr(self.__line_num)
        repr_raw_code = repr(self.__raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_line_num, repr_raw_code)


class FROMInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(FROMInstruction, self).__init__(line_num, raw_code)


class RUNInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(RUNInstruction, self).__init__(line_num, raw_code)


class CMDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(CMDInstruction, self).__init__(line_num, raw_code)


class LABELInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(LABELInstruction, self).__init__(line_num, raw_code)


class EXPOSEInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(EXPOSEInstruction, self).__init__(line_num, raw_code)


class ENVInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(ENVInstruction, self).__init__(line_num, raw_code)


class ADDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(ADDInstruction, self).__init__(line_num, raw_code)


class COPYInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(COPYInstruction, self).__init__(line_num, raw_code)


class ENTRYPOINTInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(ENTRYPOINTInstruction, self).__init__(line_num, raw_code)


class VOLUMEInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(VOLUMEInstruction, self).__init__(line_num, raw_code)


class USERInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(USERInstruction, self).__init__(line_num, raw_code)


class WORKDIRInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(WORKDIRInstruction, self).__init__(line_num, raw_code)


class ARGInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(ARGInstruction, self).__init__(line_num, raw_code)


class ONBUILDInstruction(Instruction):
    __REPR_FORMAT: str = "{0}(param_instructions={1}, line_num={2}, raw_code={3})"

    def __init__(self, param_instructions: List[Instruction], line_num: int, raw_code: str):
        super(ONBUILDInstruction, self).__init__(line_num, raw_code)
        self.__param_instructions: List[Instruction] = param_instructions

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_param_instructions = repr(self.__param_instructions)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_param_instructions, repr_line_num, repr_raw_code)

class STOPSIGNALInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(STOPSIGNALInstruction, self).__init__(line_num, raw_code)


class HEALTHCHECKInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(HEALTHCHECKInstruction, self).__init__(line_num, raw_code)


class SHELLInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(SHELLInstruction, self).__init__(line_num, raw_code)


class DockerImage:
    def __init__(self, name, tag = None, digest = None, as_name = None):
        self.__name = name
        self.__tag = tag
        self.__digest = digest
        self.__as_name = name
