from typing import Tuple, List

import dockerfile

from dockerfile_ast import DockerfileAST
from dockerfile_ast.dockerfile_items.nodes import ADDInstruction
from dockerfile_ast.dockerfile_items.nodes import ARGInstruction
from dockerfile_ast.dockerfile_items.nodes import CMDInstruction
from dockerfile_ast.dockerfile_items.nodes import COPYInstruction
from dockerfile_ast.dockerfile_items.nodes import ENTRYPOINTInstruction
from dockerfile_ast.dockerfile_items.nodes import ENVInstruction
from dockerfile_ast.dockerfile_items.nodes import EXPOSEInstruction
from dockerfile_ast.dockerfile_items.nodes import FROMInstruction
from dockerfile_ast.dockerfile_items.nodes import HEALTHCHECKInstruction
from dockerfile_ast.dockerfile_items.nodes import Instruction
from dockerfile_ast.dockerfile_items.nodes import LABELInstruction
from dockerfile_ast.dockerfile_items.nodes import ONBUILDInstruction
from dockerfile_ast.dockerfile_items.nodes import RUNInstruction
from dockerfile_ast.dockerfile_items.nodes import SHELLInstruction
from dockerfile_ast.dockerfile_items.nodes import STOPSIGNALInstruction
from dockerfile_ast.dockerfile_items.nodes import USERInstruction
from dockerfile_ast.dockerfile_items.nodes import VOLUMEInstruction
from dockerfile_ast.dockerfile_items.nodes import WORKDIRInstruction
from dockerfile_ast.dockerfile_items.utils import InstructionEnum


class DockerfileParser:
    def __init__(
            self,
            ignore_label_instructions: bool = False,
            parse_level: int = 1,
            separate_instructions: bool = False,
            separate_run_instructions: bool = False
    ):
        self.__ignore_label_instructions: bool = ignore_label_instructions
        if parse_level < 1 or 1 < parse_level:
            raise ValueError("Illegal parse_level value (> 0): {0}".format(str(parse_level)))
        self.__parse_level: int = parse_level
        self.__separate_instructions: bool = separate_instructions
        self.__separate_run_instructions: bool = separate_run_instructions

        self.__raw_code: str = None
        self.__cst: Tuple[dockerfile.Command] = None

    def __repr__(self):
        repr_format = ""

    def parse(self, raw_code: str) -> DockerfileAST:
        self.__raw_code = raw_code
        self.__cst = dockerfile.parse_string(raw_code)
        return self.__parse_instructions()

    def parse_file(self, filename: str) -> DockerfileAST:
        with open(filename) as fp:
            self.__raw_code = fp.read()
        self.__cst = dockerfile.parse_file(filename)
        return self.__parse_instructions()

    def __parse_instructions(self) -> DockerfileAST:
        instructions: List[Instruction] = list()
        for cst_instruction in self.__cst:
            tmp: List[Instruction] = self.__parse_instruction(cst_instruction)
            if tmp is not None:
                instructions.extend(tmp)
        return DockerfileAST(instructions, self.__raw_code)

    def __parse_instruction(self, cst_instruction: dockerfile.Command) -> List[Instruction]:
        instruction_enum = InstructionEnum.of(cst_instruction.cmd)
        if instruction_enum == InstructionEnum.FROM:
            # FROM Instruction
            return self.__parse_from_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.RUN:
            # RUN Instruction
            return self.__parse_run_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.CMD:
            # CMD Instruction
            return self.__parse_cmd_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.LABEL:
            # LABEL Instruction
            if self.__ignore_label_instructions:
                # Ignore this instruction if you do not need LABEL Instructions
                return None
            return self.__parse_label_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.MAINTAINER:
            # MAINTAINER Instruction (deprecated)
            if self.__ignore_label_instructions:
                # Ignore this instruction if you do not need MAINTAINER Instructions
                return None
            return self.__parse_maintainer_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.EXPOSE:
            # EXPOSE Instruction
            return self.__parse_expose_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.ENV:
            # ENV Instruction
            return self.__parse_env_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.ADD:
            # ADD Instruction
            return self.__parse_add_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.COPY:
            # COPY Instruction
            return self.__parse_add_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.ENTRYPOINT:
            # ENTRYPOINT Instruction
            return self.__parse_expose_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.VOLUME:
            # VOLUME Instruction
            return self.__parse_volume_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.USER:
            # USER Instruction
            return self.__parse_user_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.WORKDIR:
            # WORKDIR Instruction
            return self.__parse_workdir_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.ARG:
            # ARG Instruction
            return self.__parse_arg_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.ONBUILD:
            # ONBUILD Instruction
            return self.__parse_onbuild_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.STOPSIGNAL:
            # STOPSIGNAL Instruction
            return self.__parse_stopsignal_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.HEALTHCHECK:
            # HEALTHCHECK Instruction
            return self.__parse_healthcheck_instruction(cst_instruction)
        elif instruction_enum == InstructionEnum.SHELL:
            # SHELL Instruction
            return self.__parse_shell_instruction(cst_instruction)
        else:
            return [Instruction(cst_instruction.start_line, cst_instruction.original)]

    def __parse_from_instruction(self, cst_instruction: dockerfile.Command) -> List[FROMInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        FROM [--platform=<platform>] <image> [AS <name>]
        FROM [--platform=<platform>] <image>[:<tag>] [AS <name>]
        FROM [--platform=<platform>] <image>[@<digest>] [AS <name>]
        """

        return [FROMInstruction(line_num, raw_code)]

    def __parse_run_instruction(self, cst_instruction: dockerfile.Command) -> List[RUNInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        RUN <command>  # shell form (RUN ["/bin/sh", "-c", <command>])
        RUN ["executable", "param1", "param2"]  # exec form
        """

        return [RUNInstruction(line_num, raw_code)]

    def __parse_cmd_instruction(self, cst_instruction: dockerfile.Command) -> List[CMDInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        CMD ["executable","param1","param2"]  # exec form
        CMD ["param1","param2"]  # as default parameters to ENTRYPOINT
        CMD command param1 param2  # shell form
        """

        return [CMDInstruction(line_num, raw_code)]

    def __parse_label_instruction(self, cst_instruction: dockerfile.Command) -> List[LABELInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        LABEL <key>=<value> <key>=<value> <key>=<value> ...
        """

        return [LABELInstruction(line_num, raw_code)]

    def __parse_maintainer_instruction(self, cst_instruction: dockerfile.Command) -> List[LABELInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        MAINTAINER <name>
        # LABEL maintainer=<name>
        """

        return [LABELInstruction(line_num, raw_code)]

    def __parse_expose_instruction(self, cst_instruction: dockerfile.Command) -> List[EXPOSEInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        EXPOSE <port> [<port>/<protocol>...]
        """

        return [EXPOSEInstruction(line_num, raw_code)]

    def __parse_env_instruction(self, cst_instruction: dockerfile.Command) -> List[ENVInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        ENV <key>=<value> ...
        ENV MY_VAR my-value
        """

        return [ENVInstruction(line_num, raw_code)]

    def __parse_add_instruction(self, cst_instruction: dockerfile.Command) -> List[ADDInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        ADD [--chown=<user>:<group>] <src>... <dest>
        ADD [--chown=<user>:<group>] ["<src>",... "<dest>"]
        """

        return [ADDInstruction(line_num, raw_code)]

    def __parse_copy_instruction(self, cst_instruction: dockerfile.Command) -> List[COPYInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        COPY [--chown=<user>:<group>] <src>... <dest>
        COPY [--chown=<user>:<group>] ["<src>",... "<dest>"]
        """

        return [COPYInstruction(line_num, raw_code)]

    def __parse_entrypoint_instruction(self, cst_instruction: dockerfile.Command) -> List[ENTRYPOINTInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        ENTRYPOINT ["executable", "param1", "param2"]  # exec form
        ENTRYPOINT command param1 param2 # shell form
        """

        return [ENTRYPOINTInstruction(line_num, raw_code)]

    def __parse_volume_instruction(self, cst_instruction: dockerfile.Command) -> List[VOLUMEInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        VOLUME ["/data"]
        VOLUME /data1 /data2 ..
        """

        return [VOLUMEInstruction(line_num, raw_code)]

    def __parse_user_instruction(self, cst_instruction: dockerfile.Command) -> List[USERInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        USER <user>[:<group>]
        USER <UID>[:<GID>]
        """

        return [USERInstruction(line_num, raw_code)]

    def __parse_workdir_instruction(self, cst_instruction: dockerfile.Command) -> List[WORKDIRInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        WORKDIR /path/to/workdir
        """

        return [WORKDIRInstruction(line_num, raw_code)]

    def __parse_arg_instruction(self, cst_instruction: dockerfile.Command) -> List[ARGInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        ARG <name>[=<default value>]
        """

        return [ARGInstruction(line_num, raw_code)]

    def __parse_onbuild_instruction(self, cst_instruction: dockerfile.Command) -> List[ONBUILDInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        ONBUILD <INSTRUCTION>
        """

        return [ONBUILDInstruction(line_num, raw_code)]

    def __parse_stopsignal_instruction(self, cst_instruction: dockerfile.Command) -> List[STOPSIGNALInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        STOPSIGNAL signal
        """

        return [STOPSIGNALInstruction(line_num, raw_code)]

    def __parse_healthcheck_instruction(self, cst_instruction: dockerfile.Command) -> List[HEALTHCHECKInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        HEALTHCHECK [OPTIONS] CMD command
        HEALTHCHECK NONE
        """

        return [HEALTHCHECKInstruction(line_num, raw_code)]

    def __parse_shell_instruction(self, cst_instruction: dockerfile.Command) -> List[SHELLInstruction]:
        line_num: int = cst_instruction.start_line
        raw_code: str = cst_instruction.original

        """
        SHELL ["executable", "parameters"]
        """

        return [SHELLInstruction(line_num, raw_code)]
