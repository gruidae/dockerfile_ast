import dockerfile

from dfile.utils import InstructionEnum


class Instruction:
    def __init__(self, line_num: int, raw_code: str):
        self.__line_num = line_num
        self.__raw_code = raw_code

    @property
    def raw_code(self):
        return self.__raw_code

    def __repr__(self):
        return "{0}(line_num={1}, raw_code={2})".format(self.__class__.__name__, repr(self.__line_num), repr(self.__raw_code))

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        instruction_enum = InstructionEnum.of(cst_instruction.cmd)
        if instruction_enum == InstructionEnum.FROM:
            return FROMInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.RUN:
            return RUNInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.CMD:
            return CMDInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.LABEL:
            return LABELInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.MAINTAINER:
            return LABELInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.EXPOSE:
            return EXPOSEInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.ENV:
            return ENVInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.ADD:
            return ADDInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.COPY:
            return COPYInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.ENTRYPOINT:
            return ENTRYPOINTInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.VOLUME:
            return VOLUMEInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.USER:
            return USERInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.ARG:
            return ARGInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.ONBUILD:
            return ONBUILDInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.STOPSIGNAL:
            return STOPSIGNALInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.HEALTHCHECK:
            return HEALTHCHECKInstruction.generate(cst_instruction)
        elif instruction_enum == InstructionEnum.SHELL:
            return SHELLInstruction.generate(cst_instruction)
        else:
            return Instruction(cst_instruction.start_line, cst_instruction.original)


class FROMInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = FROMInstruction(line_num, raw_code)
        return instruction


class RUNInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = RUNInstruction(line_num, raw_code)
        return instruction


class CMDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = CMDInstruction(line_num, raw_code)
        return instruction


class LABELInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = LABELInstruction(line_num, raw_code)
        return instruction


class EXPOSEInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = EXPOSEInstruction(line_num, raw_code)
        return instruction


class ENVInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = ENVInstruction(line_num, raw_code)
        return instruction


class ADDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = ADDInstruction(line_num, raw_code)
        return instruction


class COPYInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = COPYInstruction(line_num, raw_code)
        return instruction


class ENTRYPOINTInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = ENTRYPOINTInstruction(line_num, raw_code)
        return instruction


class VOLUMEInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = VOLUMEInstruction(line_num, raw_code)
        return instruction


class USERInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = USERInstruction(line_num, raw_code)
        return instruction


class WORKDIRInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = WORKDIRInstruction(line_num, raw_code)
        return instruction


class ARGInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = ARGInstruction(line_num, raw_code)
        return instruction


class ONBUILDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = ONBUILDInstruction(line_num, raw_code)
        return instruction


class STOPSIGNALInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = STOPSIGNALInstruction(line_num, raw_code)
        return instruction


class HEALTHCHECKInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = HEALTHCHECKInstruction(line_num, raw_code)
        return instruction


class SHELLInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super().__init__(line_num, raw_code)

    @staticmethod
    def generate(cst_instruction: dockerfile.Command):
        line_num = cst_instruction.start_line
        raw_code = cst_instruction.original
        instruction = HEALTHCHECKInstruction(line_num, raw_code)
        return instruction
