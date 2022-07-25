import re
from typing import Dict, List, Tuple

import dockerfile
from dockerfile import GoParseError

from dockerfile_ast import DockerfileAST
from dockerfile_ast.dockerfile_items.bash_items.nodes import EnvironmentVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import TemporaryVariable
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
    __CHAINING_ONBUILD_ERROR_MESSAGE = "Chaining ONBUILD instructions using ONBUILD ONBUILD isn’t allowed."
    __HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE = "Sub command of HEALTHCHECK instruction is only \"None\" or \"CMD\"."
    __PARSE_ERROR_FORMAT = "{0}: {1}"
    __PARSE_ERROR_FORMAT_FILENAME = "{0}: {1}: {2}"

    def __init__(
            self,
            exclude_label_instructions: bool = False,
            parse_level: int = 1,
            separate_instructions: bool = False,
            separate_run_instructions: bool = False
    ):
        self.__exclude_label_instructions: bool = exclude_label_instructions
        if parse_level < 1 or 1 < parse_level:
            raise ValueError("Illegal parse_level value (> 0): {0}".format(str(parse_level)))
        self.__parse_level: int = parse_level
        self.__separate_instructions: bool = separate_instructions
        self.__separate_run_instructions: bool = separate_run_instructions

        self.__filename: str = None
        self.__raw_code: str = None
        self.__cst: Tuple[dockerfile.Command] = None

        self.__arg_variables: Dict[str, TemporaryVariable] = None  # ARG変数の辞書型（変数名がキー）
        self.__env_variables: Dict[str, EnvironmentVariable] = None  # ENV変数の辞書型（変数名がキー）

    def parse(self, raw_code: str) -> DockerfileAST:
        self.__filename = None
        self.__raw_code = raw_code
        self.__cst = dockerfile.parse_string(raw_code)
        self.__arg_variables: List[TemporaryVariable] = list()
        self.__env_variables: List[EnvironmentVariable] = list()
        return self.__parse_instructions()

    def parse_file(self, filename: str) -> DockerfileAST:
        self.__filename = filename
        with open(filename) as fp:
            self.__raw_code = fp.read()
        self.__cst = dockerfile.parse_file(filename)
        self.__arg_variables = dict()
        self.__env_variables = dict()
        return self.__parse_instructions()

    def __parse_instructions(self) -> DockerfileAST:
        instructions: List[Instruction] = list()
        for cst_instruction in self.__cst:
            tmp: List[Instruction] = self.__parse_instruction(cst_instruction)
            if tmp is not None:
                # Skip instructions not subject to parse
                instructions.extend(tmp)
        return DockerfileAST(instructions, self.__raw_code)

    def __parse_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int = 0) -> List[Instruction]:
        instruction_enum = InstructionEnum.of(cst_instruction.cmd)
        if instruction_enum == InstructionEnum.FROM:
            # FROM instruction
            return self.__parse_from_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.RUN:
            # RUN instruction
            return self.__parse_run_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.CMD:
            # CMD instruction
            return self.__parse_cmd_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.LABEL:
            # LABEL instruction
            if self.__exclude_label_instructions:
                # Skip parsing this instruction if you do not need LABEL instructions
                return None
            return self.__parse_label_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.MAINTAINER:
            # MAINTAINER instruction (deprecated)
            if self.__exclude_label_instructions:
                # Skip parsing this instruction if you do not need MAINTAINER instructions
                return None
            return self.__parse_maintainer_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.EXPOSE:
            # EXPOSE instruction
            return self.__parse_expose_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.ENV:
            # ENV instruction
            return self.__parse_env_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.ADD:
            # ADD instruction
            return self.__parse_add_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.COPY:
            # COPY instruction
            return self.__parse_add_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.ENTRYPOINT:
            # ENTRYPOINT instruction
            return self.__parse_expose_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.VOLUME:
            # VOLUME instruction
            return self.__parse_volume_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.USER:
            # USER instruction
            return self.__parse_user_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.WORKDIR:
            # WORKDIR instruction
            return self.__parse_workdir_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.ARG:
            # ARG instruction
            return self.__parse_arg_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.ONBUILD:
            # ONBUILD instruction
            return self.__parse_onbuild_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.STOPSIGNAL:
            # STOPSIGNAL instruction
            return self.__parse_stopsignal_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.HEALTHCHECK:
            # HEALTHCHECK instruction
            return self.__parse_healthcheck_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.SHELL:
            # SHELL instruction
            return self.__parse_shell_instruction(cst_instruction, line_num_offset)
        else:
            return [Instruction(cst_instruction.start_line + line_num_offset, cst_instruction.original)]

    def __parse_from_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[FROMInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        FROM [--platform=<platform>] <image> [AS <name>]
        FROM [--platform=<platform>] <image>[:<tag>] [AS <name>]
        FROM [--platform=<platform>] <image>[@<digest>] [AS <name>]
        """

        return [FROMInstruction(line_num + line_num_offset, raw_code)]

    def __parse_run_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[RUNInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        RUN <command>  # shell form (RUN ["/bin/sh", "-c", <command>])
        RUN ["executable", "param1", "param2"]  # exec form
        """

        return [RUNInstruction(line_num, raw_code)]

    def __parse_cmd_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[CMDInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        CMD ["executable","param1","param2"]  # exec form
        CMD ["param1","param2"]  # as default parameters to ENTRYPOINT
        CMD command param1 param2  # shell form
        """

        return [CMDInstruction(line_num, raw_code)]

    def __parse_label_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[LABELInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        LABEL <key>=<value> <key>=<value> <key>=<value> ...
        """

        return [LABELInstruction(line_num, raw_code)]

    def __parse_maintainer_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[LABELInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        MAINTAINER <name>
        # LABEL maintainer=<name>
        """

        return [LABELInstruction(line_num, raw_code)]

    def __parse_expose_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[EXPOSEInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        EXPOSE <port> [<port>/<protocol>...]
        """

        return [EXPOSEInstruction(line_num, raw_code)]

    def __parse_env_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ENVInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        ENV <key>=<value> ...
        ENV MY_VAR my-value
        """

        return [ENVInstruction(line_num, raw_code)]

    def __parse_add_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ADDInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        ADD [--chown=<user>:<group>] <src>... <dest>
        ADD [--chown=<user>:<group>] ["<src>",... "<dest>"]
        """

        return [ADDInstruction(line_num, raw_code)]

    def __parse_copy_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[COPYInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        COPY [--chown=<user>:<group>] <src>... <dest>
        COPY [--chown=<user>:<group>] ["<src>",... "<dest>"]
        """

        return [COPYInstruction(line_num, raw_code)]

    def __parse_entrypoint_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ENTRYPOINTInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        ENTRYPOINT ["executable", "param1", "param2"]  # exec form
        ENTRYPOINT command param1 param2 # shell form
        """

        return [ENTRYPOINTInstruction(line_num, raw_code)]

    def __parse_volume_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[VOLUMEInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        VOLUME ["/data"]
        VOLUME /data1 /data2 ..
        """

        return [VOLUMEInstruction(line_num, raw_code)]

    def __parse_user_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[USERInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        USER <user>[:<group>]
        USER <UID>[:<GID>]
        """

        return [USERInstruction(line_num, raw_code)]

    def __parse_workdir_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[WORKDIRInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        WORKDIR /path/to/workdir
        """

        return [WORKDIRInstruction(line_num, raw_code)]

    def __parse_arg_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ARGInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        ARG <name>[=<default value>]
        """

        return [ARGInstruction(line_num, raw_code)]

    def __parse_onbuild_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ONBUILDInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        if InstructionEnum.of(cst_instruction.sub_cmd) == InstructionEnum.ONBUILD:
            # Chaining ONBUILD error
            if self.__filename is None:
                error_message = self.__PARSE_ERROR_FORMAT.format(
                    line_num, self.__CHAINING_ONBUILD_ERROR_MESSAGE
                )
                raise GoParseError(error_message)
            else:
                error_message = self.__PARSE_ERROR_FORMAT_FILENAME.format(
                    self.__filename, line_num, self.__CHAINING_ONBUILD_ERROR_MESSAGE
                )
                raise GoParseError(error_message)

        # Reformat parameters on ONBUILD instruction
        param = re.sub(r"^[Oo][Nn][Bb][Uu][Ii][Ll][Dd]\s+", "", raw_code)

        # generate CST of an instruction this ONBUILD instruction has as a parameter
        param_cst_instruction: dockerfile.Command = dockerfile.parse_string(param)[0]
        param_instructions: List[Instruction] = self.__parse_instruction(param_cst_instruction, line_num - 1)
        return [ONBUILDInstruction(param_instructions, line_num, raw_code)]

    def __parse_stopsignal_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[STOPSIGNALInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        STOPSIGNAL signal
        """

        return [STOPSIGNALInstruction(line_num, raw_code)]

    def __parse_healthcheck_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[HEALTHCHECKInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        TODO: parse options
            --interval=DURATION (default: 30s)
            --timeout=DURATION (default: 30s)
            --start-period=DURATION (default: 0s)
            --retries=N (default: 3)
        """

        try:
            if InstructionEnum.of(cst_instruction.sub_cmd) != InstructionEnum.CMD:
                # Sub command of HEALTHCHECK error
                if self.__filename is None:
                    error_message = self.__PARSE_ERROR_FORMAT.format(
                        line_num, self.__HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE
                    )
                    raise GoParseError(error_message)
                else:
                    error_message = self.__PARSE_ERROR_FORMAT_FILENAME.format(
                        self.__filename, line_num, self.__HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE
                    )
                    raise GoParseError(error_message)
        except ValueError:
            if not re.match(cst_instruction.sub_cmd, r"[Nn][Oo][Nn][Ee]"):
                if self.__filename is None:
                    error_message = self.__PARSE_ERROR_FORMAT.format(
                        line_num, self.__HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE
                    )
                    raise GoParseError(error_message)
                else:
                    error_message = self.__PARSE_ERROR_FORMAT_FILENAME.format(
                        self.__filename, line_num, self.__HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE
                    )
                    raise GoParseError(error_message)

        # Reformat parameters on HEALTHCHECK instruction
        param = re.sub(r"^[Hh][Ee][Aa][Ll][Tt][Hh][Cc][Hh][Ee][Cc][Kk]\s+", "", raw_code)

        # generate CST of an instruction this HEALTHCHECK instruction has as a parameter
        if re.match(param, r"[Nn][Oo][Nn][Ee]"):
            param_instructions = None
        else:
            param_cst_instruction: dockerfile.Command = dockerfile.parse_string(param)[0]
            param_instructions: List[Instruction] = self.__parse_instruction(param_cst_instruction, line_num - 1)
        return [HEALTHCHECKInstruction(param_instructions, line_num, raw_code)]

    def __parse_shell_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[SHELLInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        SHELL ["executable", "parameters"]
        """

        return [SHELLInstruction(line_num, raw_code)]
