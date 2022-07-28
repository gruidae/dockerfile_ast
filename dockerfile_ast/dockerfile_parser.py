import logging
import re
from typing import Dict, List, Tuple

import dockerfile
from dockerfile import GoParseError

import dockerfile_ast.utils
from dockerfile_ast import DockerfileAST, Instruction
from dockerfile_ast.bash_parser import BashParser
from dockerfile_ast.dockerfile_items.bash_items.nodes import BashValueNode
from dockerfile_ast.dockerfile_items.bash_items.nodes import BuildTimeVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import EnvironmentVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import Filepath
from dockerfile_ast.dockerfile_items.bash_items.nodes import SystemCallSignal
import dockerfile_ast.dockerfile_items.bash_items.utils
from dockerfile_ast.dockerfile_items.nodes import DockerLabel
from dockerfile_ast.dockerfile_items.nodes import DockerPort
from dockerfile_ast.dockerfile_items.instructions import FROMInstruction, RUNInstruction
from dockerfile_ast.dockerfile_items.instructions import CMDInstruction
from dockerfile_ast.dockerfile_items.instructions import LABELInstruction
from dockerfile_ast.dockerfile_items.instructions import EXPOSEInstruction
from dockerfile_ast.dockerfile_items.instructions import ENVInstruction
from dockerfile_ast.dockerfile_items.instructions import ADDInstruction
from dockerfile_ast.dockerfile_items.instructions import COPYInstruction
from dockerfile_ast.dockerfile_items.instructions import ENTRYPOINTInstruction
from dockerfile_ast.dockerfile_items.instructions import VOLUMEInstruction
from dockerfile_ast.dockerfile_items.instructions import USERInstruction
from dockerfile_ast.dockerfile_items.instructions import WORKDIRInstruction
from dockerfile_ast.dockerfile_items.instructions import ARGInstruction
from dockerfile_ast.dockerfile_items.instructions import ONBUILDInstruction
from dockerfile_ast.dockerfile_items.instructions import STOPSIGNALInstruction
from dockerfile_ast.dockerfile_items.instructions import HEALTHCHECKInstruction
from dockerfile_ast.dockerfile_items.instructions import SHELLInstruction
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
            self.__logger: logging.Logger = dockerfile_ast.utils.init_logger(logging.WARNING, None, logging.WARNING)
        else:
            self.__logger: logging.Logger = logger

        self.__filename: str = None
        self.__raw_code: str = None
        self.__cst: Tuple[dockerfile.Command] = None
        # ARG変数の辞書型（変数名がキー）
        self.__arg_variables: Dict[str, BuildTimeVariable] = dict()
        # ENV変数の辞書型（変数名がキー）
        self.__env_variables: Dict[str, EnvironmentVariable] \
            = dockerfile_ast.dockerfile_items.bash_items.utils.init_environment_variables()

    def parse(self, raw_code: str) -> DockerfileAST:
        self.__filename = None
        self.__raw_code = raw_code
        self.__cst = dockerfile.parse_string(raw_code)
        self.__arg_variables = dict()
        self.__env_variables = dockerfile_ast.dockerfile_items.bash_items.utils.init_environment_variables()
        return self.__parse_instructions()

    def parse_file(self, filename: str) -> DockerfileAST:
        self.__filename = filename
        with open(filename) as fp:
            self.__raw_code = fp.read()
        self.__cst = dockerfile.parse_file(filename)
        self.__arg_variables = dict()
        self.__env_variables = dockerfile_ast.dockerfile_items.bash_items.utils.init_environment_variables()
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
                # Skip parsing this instruction if you do not would like LABEL Instructions
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
            return self.__parse_copy_instruction(cst_instruction, line_num_offset)
        elif instruction_enum == InstructionEnum.ENTRYPOINT:
            # ENTRYPOINT instruction
            return self.__parse_entrypoint_instruction(cst_instruction, line_num_offset)
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
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        docker_ports: List[DockerPort] = list()
        instructions: List[EXPOSEInstruction] = list()
        for str_value in cst_instruction.value:
            tokens: str = str_value.split("/")
            if len(tokens) < 2:
                port_num: BashValueNode = BashParser.simple_parse_bash_concat(
                    str_value, self.__arg_variables, self.__env_variables
                )
                protocol = None
                docker_ports.append(DockerPort(port_num, protocol))
            elif len(tokens[1]) < 1:
                _raise_go_parse_error("Protocol is not declared.", line_num, self.__filename)
            else:
                port_num: BashValueNode = BashParser.simple_parse_bash_concat(
                    tokens[0], self.__arg_variables, self.__env_variables
                )
                protocol: BashValueNode = BashParser.simple_parse_bash_concat(
                    tokens[1], self.__arg_variables, self.__env_variables
                )
                docker_ports.append(DockerPort(port_num, protocol))
            if self.__separate_instructions:
                instructions.append(EXPOSEInstruction(docker_ports, line_num, raw_code))
                docker_ports.clear()
        if not self.__separate_instructions:
            instructions.append(EXPOSEInstruction(docker_ports, line_num, raw_code))
        return instructions

    def __parse_env_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ENVInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        instructions: List[ENVInstruction] = list()
        variables: List[EnvironmentVariable] = list()

        param_iterator = iter(cst_instruction.value)
        for variable_name, str_value in zip(param_iterator, param_iterator):
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
        # Todo: Need to implement parse options `--chown=<user>:<group>`
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original
        source_filepath, destination_filepaths = _parse_source_and_destination_filepaths(
            cst_instruction.value, self.__arg_variables, self.__env_variables
        )
        return [ADDInstruction(source_filepath, destination_filepaths, line_num, raw_code)]

    def __parse_copy_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[COPYInstruction]:
        # Todo: Need to implement parse options `--chown=<user>:<group>`
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original
        source_filepath, destination_filepaths = _parse_source_and_destination_filepaths(
            cst_instruction.value, self.__arg_variables, self.__env_variables
        )
        return [COPYInstruction(source_filepath, destination_filepaths, line_num, raw_code)]

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
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        filepaths: List[Filepath] = list()
        instructions: List[VOLUMEInstruction] = list()
        for str_value in cst_instruction.value:
            value: BashValueNode = BashParser.simple_parse_bash_concat(
                str_value, self.__arg_variables, self.__env_variables
            )
            filepaths.append(Filepath(value))
            if self.__separate_instructions:
                instructions.append(VOLUMEInstruction(filepaths, line_num, raw_code))
                filepaths.clear()
        if not self.__separate_instructions:
            instructions.append(VOLUMEInstruction(filepaths, line_num, raw_code))
        return instructions

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
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original
        value: BashValueNode = BashParser.simple_parse_bash_concat(
            cst_instruction.value[0], self.__arg_variables, self.__env_variables
        )
        return [WORKDIRInstruction(Filepath(value), line_num, raw_code)]

    def __parse_arg_instruction(self, cst_instruction: dockerfile.Command, line_num_offset: int) \
            -> List[ARGInstruction]:
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original

        # '='がある場合とない場合で処理を分岐
        if len(cst_instruction.value) < 2:
            tokens = cst_instruction.value[0].split("=")
            self.__logger.debug(tokens)
            variable_name = tokens[0]
            if len(tokens) > 1:
                # '='がある場合
                str_value = tokens[1]
            else:
                # 変数名のみ定義されている場合
                str_value = None
        else:
            variable_name = cst_instruction.value[0]
            str_value = cst_instruction.value[1]

        if variable_name in self.__env_variables.keys():
            _raise_go_parse_error(variable_name + " is Environment Variable.", line_num, self.__filename)
        elif variable_name in self.__arg_variables.keys():
            _raise_go_parse_error(variable_name + " is already declared.", line_num, self.__filename)
        # 先に右辺をparse
        value: BashValueNode = BashParser.simple_parse_bash_concat(
            str_value, self.__arg_variables, self.__env_variables
        )
        variable: BuildTimeVariable = BuildTimeVariable(variable_name, value)
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
        line_num: int = cst_instruction.start_line + line_num_offset
        raw_code: str = cst_instruction.original
        value: BashValueNode = BashParser.simple_parse_bash_concat(
            cst_instruction.value[0], self.__arg_variables, self.__env_variables
        )
        return [STOPSIGNALInstruction(SystemCallSignal(value), line_num, raw_code)]

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
            sub_command: InstructionEnum = InstructionEnum.of(cst_instruction.value[0])
            if sub_command != InstructionEnum.CMD:
                # Sub command of HEALTHCHECK error
                _raise_go_parse_error(HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE, line_num, self.__filename)
        except ValueError:
            if not re.match(r"[Nn][Oo][Nn][Ee]", cst_instruction.value[0]):
                _raise_go_parse_error(HEALTHCHECK_SUB_COMMAND_ERROR_MESSAGE, line_num, self.__filename)
        # Reformat parameters on HEALTHCHECK instruction
        param = re.sub(r"^[Hh][Ee][Aa][Ll][Tt][Hh][Cc][Hh][Ee][Cc][Kk]\s+", "", raw_code)
        for flag in cst_instruction.flags:
            param = re.sub(r"^\s*" + flag + r"\s*", "", param)

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


def _parse_source_and_destination_filepaths(
        cst_instruction_params: List[str],
        arg_variables: Dict[str, BuildTimeVariable],
        env_variables: Dict[str, EnvironmentVariable]
) -> Tuple[Filepath, List[Filepath]]:
    param_iterator = iter(cst_instruction_params)
    next_param: str = next(param_iterator)
    value: BashValueNode = BashParser.simple_parse_bash_concat(next_param, arg_variables, env_variables)
    source_filepath: Filepath = Filepath(value)

    destination_filepaths: List[Filepath] = list()
    while True:
        try:
            next_param: str = next(param_iterator)
            value: BashValueNode = BashParser.simple_parse_bash_concat(next_param, arg_variables, env_variables)
            destination_filepaths.append(Filepath(value))
        except StopIteration:
            break
    return source_filepath, destination_filepaths


def _raise_go_parse_error(msg: str, line_num: int, filename: str = None):
    if filename is None:
        PARSE_ERROR_FORMAT = "{0}: {1}"
        error_message = PARSE_ERROR_FORMAT.format(line_num, msg)
    else:
        PARSE_ERROR_FORMAT_FILENAME = "{0}: {1}: {2}"
        error_message = PARSE_ERROR_FORMAT_FILENAME.format(filename, line_num, msg)
    raise GoParseError(error_message)
