import logging
import re
from typing import Dict, List, Tuple

import dockerfile
from dockerfile import GoParseError

import dockerfile_ast.util
from dockerfile_ast import DockerfileAST
from dockerfile_ast.bash_parser import BashParser
from dockerfile_ast.dockerfile_items.bash_items.nodes import BashValueNode
from dockerfile_ast.dockerfile_items.bash_items.nodes import EnvironmentVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import TemporaryVariable
from dockerfile_ast.dockerfile_items.nodes import ADDInstruction
from dockerfile_ast.dockerfile_items.nodes import ARGInstruction
from dockerfile_ast.dockerfile_items.nodes import CMDInstruction
from dockerfile_ast.dockerfile_items.nodes import COPYInstruction
from dockerfile_ast.dockerfile_items.nodes import DockerLabel
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
    """
    A parser of Dockerfile.
    """
    def __init__(
            self,
            exclude_label_instructions: bool = False,
            parse_level: int = 1,
            separate_instructions: bool = False,
            separate_run_instructions: bool = False,
            logger: logging.Logger = None
    ):
        self.__exclude_label_instructions: bool = exclude_label_instructions
        if parse_level < 1 or 1 < parse_level:
            raise ValueError("Illegal parse_level value (> 0): {0}".format(str(parse_level)))
        self.__parse_level: int = parse_level
        self.__separate_instructions: bool = separate_instructions
        self.__separate_run_instructions: bool = separate_run_instructions
        if logger is None:
            self.__logger: logging.Logger = dockerfile_ast.util.init_logger(logging.WARNING, None, logging.WARNING)
        else:
            self.__logger: logging.Logger = logger

        self.__filename: str = None
        self.__raw_code: str = None
        self.__cst: Tuple[dockerfile.Command] = None

        self.__arg_variables: Dict[str, TemporaryVariable] = dict()  # ARG変数の辞書型（変数名がキー）
        self.__env_variables: Dict[str, EnvironmentVariable] = dict()  # ENV変数の辞書型（変数名がキー）

    def parse(self, raw_code: str) -> DockerfileAST:
        self.__filename = None
        self.__raw_code = raw_code
        self.__cst = dockerfile.parse_string(raw_code)
        self.__arg_variables = dict()
        self.__env_variables = dict()
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
            if tmp is None:
                # Skip instructions not subject to parse
                continue
            instructions.extend(tmp)
        return DockerfileAST(instructions, self.__raw_code)

    def __parse_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int = 0) -> List[Instruction]:
        self.__logger.debug(repr(cst_instruction))
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
                # Skip parsing this instruction if you do not need LABEL Instructions
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
        # TODO: Need to implement
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
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        RUN <command>  # shell form (RUN ["/bin/sh", "-c", <command>])
        RUN ["executable", "param1", "param2"]  # exec form
        """

        return [RUNInstruction(line_num, raw_code)]

    def __parse_cmd_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[CMDInstruction]:
        # TODO: Need to implement
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

        instructions: List[LABELInstruction] = list()
        docker_labels: List[DockerLabel] = list()

        # イテレータを使ってリストから2個ずつ取得（変数名->変数の値の順で格納されているため）
        value_iterator = iter(cst_instruction.value)
        for label_name, str_value in zip(value_iterator, value_iterator):
            label_value: BashValueNode = BashParser.simple_parse_bash_concat(
                str_value, self.__arg_variables, self.__env_variables
            )
            docker_labels.append(DockerLabel(label_name, label_value))
            if self.__separate_instructions:
                instructions.append(LABELInstruction(docker_labels, line_num, raw_code))
                docker_labels.clear()
        if not self.__separate_instructions:
            instructions.append(LABELInstruction(docker_labels, line_num, raw_code))
        return instructions

    def __parse_maintainer_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[LABELInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        maintainer_name: BashValueNode = BashParser.simple_parse_bash_concat(
            cst_instruction.value[0], self.__arg_variables, self.__env_variables
        )
        docker_label: DockerLabel = DockerLabel(DockerLabel.MAINTAINER_NAME, maintainer_name)
        return [LABELInstruction([docker_label], line_num, raw_code)]

    def __parse_expose_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[EXPOSEInstruction]:
        # TODO: Need to implement
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

        instructions: List[ENVInstruction] = list()
        variables: List[Dict[EnvironmentVariable, BashValueNode]] = list()

        value_iterator = iter(cst_instruction.value)
        for variable_name, str_value in zip(value_iterator, value_iterator):
            # 右辺の変数代入値からparse
            variable_value: BashValueNode = BashParser.simple_parse_bash_concat(
                str_value, self.__arg_variables, self.__env_variables
            )

            # 宣言済みか否かにかかわらず，新しくENV変数ノードを追加．
            variable: EnvironmentVariable = EnvironmentVariable(variable_name, variable_value)
            self.__env_variables[variable_name] = variable
            variables.append(variable)
            if self.__separate_instructions:
                instructions.append(ENVInstruction(variables, line_num, raw_code))
                variables.clear()
        if not self.__separate_instructions:
            instructions.append(ENVInstruction(variables, line_num, raw_code))
        return instructions

    def __parse_add_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ADDInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        ADD [--chown=<user>:<group>] <src>... <dest>
        ADD [--chown=<user>:<group>] ["<src>",... "<dest>"]
        """

        return [ADDInstruction(line_num, raw_code)]

    def __parse_copy_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[COPYInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        COPY [--chown=<user>:<group>] <src>... <dest>
        COPY [--chown=<user>:<group>] ["<src>",... "<dest>"]
        """

        return [COPYInstruction(line_num, raw_code)]

    def __parse_entrypoint_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ENTRYPOINTInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        ENTRYPOINT ["executable", "param1", "param2"]  # exec form
        ENTRYPOINT command param1 param2 # shell form
        """

        return [ENTRYPOINTInstruction(line_num, raw_code)]

    def __parse_volume_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[VOLUMEInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        VOLUME ["/data"]
        VOLUME /data1 /data2 ..
        """

        return [VOLUMEInstruction(line_num, raw_code)]

    def __parse_user_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[USERInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        USER <user>[:<group>]
        USER <UID>[:<GID>]
        """

        return [USERInstruction(line_num, raw_code)]

    def __parse_workdir_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[WORKDIRInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        WORKDIR /path/to/workdir
        """

        return [WORKDIRInstruction(line_num, raw_code)]

    def __parse_arg_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ARGInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        # '='がある場合とない場合で処理を分岐
        if len(cst_instruction.value) < 2:
            split_tokens = cst_instruction.value[0].split("=")
            variable_name = split_tokens[0]
            if len(split_tokens) > 0:
                # '='がある場合
                str_value = split_tokens[1]
            else:
                # 変数名のみ定義されている場合
                str_value = None
        else:
            variable_name = cst_instruction.value[0]
            str_value = cst_instruction.value[1]

        # 先に右辺をparse
        value: BashValueNode = BashParser.simple_parse_bash_concat(
            str_value, self.__arg_variables, self.__env_variables
        )
        if variable_name in self.__env_variables.keys():
            _raise_go_parse_error(variable_name + " is Environment Variable.", line_num, self.__filename)
        else:
            # 宣言済みか否かにかかわらず，新しくARG変数ノードを追加．
            variable: TemporaryVariable = TemporaryVariable(variable_name, value)
            self.__arg_variables[variable_name] = variable
        return [ARGInstruction(variable, line_num, raw_code)]

    def __parse_onbuild_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ONBUILDInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        if InstructionEnum.of(cst_instruction.sub_cmd) == InstructionEnum.ONBUILD:
            # Chaining ONBUILD error
            CHAINING_ONBUILD_ERROR_MESSAGE = "Chaining ONBUILD instructions using ONBUILD ONBUILD isn’t allowed."
            _raise_go_parse_error(CHAINING_ONBUILD_ERROR_MESSAGE, line_num, self.__filename)

        # Reformat parameters on ONBUILD instruction
        param = re.sub(r"^[Oo][Nn][Bb][Uu][Ii][Ll][Dd]\s+", "", raw_code)

        # generate CST of an instruction this ONBUILD instruction has as a parameter
        param_cst_instruction: dockerfile.Command = dockerfile.parse_string(param)[0]
        param_instructions: List[Instruction] = self.__parse_instruction(param_cst_instruction, line_num - 1)
        return [ONBUILDInstruction(param_instructions, line_num, raw_code)]

    def __parse_stopsignal_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[STOPSIGNALInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        STOPSIGNAL signal
        """

        return [STOPSIGNALInstruction(line_num, raw_code)]

    def __parse_healthcheck_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[HEALTHCHECKInstruction]:
        """
        Todo: Need to implement parse options
            * --interval=DURATION (default: 30s)
            * --timeout=DURATION (default: 30s)
            * --start-period=DURATION (default: 0s)
            * --retries=N (default: 3)
        """
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE = "Sub command of HEALTHCHECK instruction is only \"None\" or \"CMD\"."
        try:
            if InstructionEnum.of(cst_instruction.sub_cmd) != InstructionEnum.CMD:
                # Sub command of HEALTHCHECK error
                _raise_go_parse_error(HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE, line_num, self.__filename)
        except ValueError:
            if not re.match(cst_instruction.sub_cmd, r"[Nn][Oo][Nn][Ee]"):
                _raise_go_parse_error(HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE, line_num, self.__filename)

        # Reformat parameters on HEALTHCHECK instruction
        param = re.sub(r"^[Hh][Ee][Aa][Ll][Tt][Hh][Cc][Hh][Ee][Cc][Kk]\s+", "", raw_code)

        # generate CST of an instruction this HEALTHCHECK instruction has as a parameter
        if re.match(r"[Nn][Oo][Nn][Ee]", param):
            param_instructions = None
        else:
            param_cst_instruction: dockerfile.Command = dockerfile.parse_string(param)[0]
            param_instructions: List[Instruction] = self.__parse_instruction(param_cst_instruction, line_num - 1)
        return [HEALTHCHECKInstruction(param_instructions, line_num, raw_code)]

    def __parse_shell_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[SHELLInstruction]:
        # TODO: Need to implement
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        """
        SHELL ["executable", "parameters"]
        """

        return [SHELLInstruction(line_num, raw_code)]


def _raise_go_parse_error(msg: str, line_num: int, filename: str = None):
    PARSE_ERROR_FORMAT = "{0}: {1}"
    PARSE_ERROR_FORMAT_FILENAME = "{0}: {1}: {2}"
    if filename is None:
        error_message = PARSE_ERROR_FORMAT.format(line_num, msg)
        raise GoParseError(error_message)
    else:
        error_message = PARSE_ERROR_FORMAT_FILENAME.format(filename, line_num, msg)
        raise GoParseError(error_message)
