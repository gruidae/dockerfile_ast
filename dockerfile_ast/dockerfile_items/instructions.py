from abc import ABCMeta
from typing import List

from dockerfile_ast.dockerfile_items.bash_items.nodes import BuildTimeVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import EnvironmentVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import Filepath
from dockerfile_ast.dockerfile_items.bash_items.nodes import SystemCallSignal
from dockerfile_ast.dockerfile_items.nodes import DockerfileSyntaxNode
from dockerfile_ast.dockerfile_items.nodes import DockerLabel
from dockerfile_ast.dockerfile_items.nodes import DockerPort
from dockerfile_ast.dockerfile_items.utils import InstructionEnum


class Instruction(DockerfileSyntaxNode, metaclass=ABCMeta):
    """
    A node of Dockerfile Instruction.

    Attributes
    ----------
    __line_num : int
        Line number of this Docker instruction.
    __raw_code : str
        Original Dockerfile source code.
    """
    __REPR_FORMAT: str = "{0}(line_num={1}, raw_code={2})"

    def __init__(self, line_num: int, raw_code: str):
        """
        Parameters
        ----------
        line_num : int
            Line number.
        raw_code : str
            Original Dockerfile source code.
        """
        super(Instruction, self).__init__()
        self.__line_num = line_num
        self.__raw_code: str = raw_code

    @property
    def line_num(self) -> int:
        """
        Returns
        -------
        __line_num : int
            Line number.
        """
        return self.__line_num

    @property
    def raw_code(self) -> str:
        """
        Returns
        -------
        __raw_code : int
            Original Dockerfile source code.
        """
        return self.__raw_code

    def __hash__(self):
        return hash(self.__line_num) + hash(self.__raw_code)

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_line_num = repr(self.__line_num)
        repr_raw_code = repr(self.__raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_line_num, repr_raw_code)

    def __str__(self):
        return self.__raw_code


class FROMInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(FROMInstruction, self).__init__(line_num, raw_code)

    """
    FROM [--platform=<platform>] <image> [AS <name>]
    FROM [--platform=<platform>] <image>[:<tag>] [AS <name>]
    FROM [--platform=<platform>] <image>[@<digest>] [AS <name>]
    """


class RUNInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(RUNInstruction, self).__init__(line_num, raw_code)

    """
    RUN <command>
    RUN ["executable", "param1", "param2"]
    """


class CMDInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(CMDInstruction, self).__init__(line_num, raw_code)

    """
    CMD ["executable","param1","param2"]
    CMD ["param1","param2"]
    CMD command param1 param2
    """


class LABELInstruction(Instruction):
    """
    A node of LABEL Instruction.

    Attributes
    ----------
    __labels : List[DockerLabel]
        List of Docker labels declared by this LABEL Instruction.
    """
    __REPR_FORMAT: str = "{0}(labels={1}, line_num={2}, raw_code={3})"

    def __init__(self, labels: List[DockerLabel], line_num: int, raw_code: str):
        """
        Parameters
        ----------
        labels : List[DockerLabel]
            List of Docker labels declared by this LABEL Instruction.
        line_num : int
            Line number of this LABEL Instruction.
        raw_code : str
            Original Dockerfile source code.
        """
        super(LABELInstruction, self).__init__(line_num, raw_code)
        self.__labels: List[DockerLabel] = labels

    @property
    def labels(self) -> List[DockerLabel]:
        """
        Returns
        -------
        __labels : List[DockerLabel]
            List of Docker labels declared by this LABEL Instruction.
        """
        return self.__labels

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_labels = repr(self.__labels)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_labels, repr_line_num, repr_raw_code)

    # override
    def __str__(self):
        return " ".join([str(InstructionEnum.LABEL)] + [str(label) for label in self.__labels])


class EXPOSEInstruction(Instruction):
    """
    A node of EXPOSE Instruction.

    Attributes
    ----------
    __ports : List[DockerPort]
        List of Docker ports declared by this EXPOSE Instruction.
    """
    __REPR_FORMAT: str = "{0}(ports={1}, line_num={2}, raw_code={3})"

    def __init__(self, ports: List[DockerPort], line_num: int, raw_code: str):
        """
        Parameters
        ----------
        ports : List[DockerPort]
            List of Docker ports declared by this LABEL Instruction.
        line_num : int
            Line number of this EXPOSE Instruction.
        raw_code : str
            Original Dockerfile source code.
        """
        super(EXPOSEInstruction, self).__init__(line_num, raw_code)
        self.__ports: List[DockerPort] = ports

    @property
    def ports(self) -> List[DockerPort]:
        """
        Returns
        -------
        __ports : List[DockerPort]
            List of Docker ports declared by this EXPOSE Instruction.
        """
        return self.__ports

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_ports = repr(self.__ports)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_ports, repr_line_num, repr_raw_code)


class ENVInstruction(Instruction):
    """
    A node of ENV Instruction.

    Attributes
    ----------
    __variables: List[EnvironmentVariable]
        List of environment variables declared by this ENV Instruction.
    """
    __REPR_FORMAT: str = "{0}(variables={1}, line_num={2}, raw_code={3})"

    def __init__(self, variables: List[EnvironmentVariable], line_num: int, raw_code: str):
        """
        Parameters
        ----------
        variables :  List[EnvironmentVariable]
            List of environment variables declared by this ENV Instruction.
        line_num : int
            Line number of this ENV Instruction.
        raw_code : str
            Original Dockerfile source code.
        """
        super(ENVInstruction, self).__init__(line_num, raw_code)
        self.__variables: List[EnvironmentVariable] = variables

    @property
    def variables(self) -> List[EnvironmentVariable]:
        """
        Returns
        -------
        __variables :  List[EnvironmentVariable]
            List of environment variables declared by this ENV Instruction.
        """
        return self.__variables

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_variables = repr(self.__variables)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_variables, repr_line_num, repr_raw_code)

    # override
    def __str__(self):
        return " ".join([str(InstructionEnum.ENV)] + [str(variable) for variable in self.variables])


class ADDInstruction(Instruction):
    """
    A node of ADD Instruction.

    Todo: Need to implement parse options `--chown=<user>:<group>`

    Attributes
    ----------
    __source: Filepath

    __destinations: List[FilePath]

    """
    __REPR_FORMAT: str = "{0}(source={1}, destinations={2}, line_num={3}, raw_code={4})"

    def __init__(self, source: Filepath, destinations: List[Filepath], line_num: int, raw_code: str):
        """
        Parameters
        ----------
        source : Filepath

        destinations : List[FilePath]

        line_num : int
            Line number of this ADD Instruction.
        raw_code : str
            Original Dockerfile source code.
        """
        super(ADDInstruction, self).__init__(line_num, raw_code)
        self.__source: Filepath = source
        self.__destinations: List[Filepath] = destinations

    @property
    def source(self) -> Filepath:
        """
        Returns
        -------
        __source: Filepath

        """
        return self.__source

    @property
    def destinations(self) -> List[Filepath]:
        """
        Returns
        -------
        __destinations: List[FilePath]

        """
        return self.__destinations

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_source = repr(self.__source)
        repr_destinations = repr(self.__destinations)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_source, repr_destinations, repr_line_num, repr_raw_code)


class COPYInstruction(Instruction):
    """
    A node of COPY Instruction.

    Todo: Need to implement parse options `--chown=<user>:<group>`

    Attributes
    ----------
    __source: Filepath

    __destinations: List[FilePath]

    """
    __REPR_FORMAT: str = "{0}(source={1}, destinations={2}, line_num={3}, raw_code={4})"

    def __init__(self, source: Filepath, destinations: List[Filepath], line_num: int, raw_code: str):
        """
        Parameters
        ----------
        source : Filepath

        destinations : List[FilePath]

        line_num : int
            Line number of this COPY Instruction.
        raw_code : str
            Original Dockerfile source code.
        """
        super(COPYInstruction, self).__init__(line_num, raw_code)
        self.__source: Filepath = source
        self.__destinations: List[Filepath] = destinations

    @property
    def source(self) -> Filepath:
        """
        Returns
        -------
        __source: Filepath

        """
        return self.__source

    @property
    def destinations(self) -> List[Filepath]:
        """
        Returns
        -------
        __destinations: List[FilePath]

        """
        return self.__destinations

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_source = repr(self.__source)
        repr_destinations = repr(self.__destinations)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_source, repr_destinations, repr_line_num, repr_raw_code)


class ENTRYPOINTInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(ENTRYPOINTInstruction, self).__init__(line_num, raw_code)

    """
    ENTRYPOINT ["executable", "param1", "param2"]
    ENTRYPOINT command param1 param2
    """


class VOLUMEInstruction(Instruction):
    """
    A node of VOLUME Instruction.

    Attributes
    ----------
    __volumes : List[Filepath]
        List of mount points created by this VOLUME Instruction.
    """
    __REPR_FORMAT: str = "{0}(volumes={1}, line_num={2}, raw_code={3})"

    def __init__(self, volumes: List[Filepath], line_num: int, raw_code: str):
        """
        Parameters
        ----------
        volumes : List[Filepath]
            List of mount points created by this VOLUME Instruction.
        line_num : int
            Line number of this VOLUME Instruction.
        raw_code : str
            Original Dockerfile code source.
        """
        super(VOLUMEInstruction, self).__init__(line_num, raw_code)
        self.__volumes: List[Filepath] = volumes

    @property
    def volumes(self) -> List[Filepath]:
        """

        Returns
        -------
        __volumes : List[Filepath]
          List of mount points created by this VOLUME Instruction.
        """
        return self.__volumes

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_volumes = repr(self.__volumes)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_volumes, repr_line_num, repr_raw_code)

    # override
    def __str__(self):
        return " ".join([str(InstructionEnum.VOLUME)] + [str(volume) for volume in self.__volumes])


class USERInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(USERInstruction, self).__init__(line_num, raw_code)

    """
    USER <user>[:<group>]
    USER <UID>[:<GID>]
    """


class WORKDIRInstruction(Instruction):
    """
    A node of WORKDIR Instruction.

    Attributes
    ----------
    __work_dir : Filepath
        Working directory declared by this WORKDIR Instruction.
    """
    __REPR_FORMAT: str = "{0}(work_dir={1}, line_num={2}, raw_code={3})"

    def __init__(self, work_dir: Filepath, line_num: int, raw_code: str):
        """
        Parameters
        ----------
        work_dir : Filepath
            Working directory declared by this WORKDIR Instruction.
        line_num : int
            Line number of this WORKDIR Instruction.
        raw_code : str
            Original Dockerfile code source.
        """
        super(WORKDIRInstruction, self).__init__(line_num, raw_code)
        self.__work_dir: Filepath = work_dir

    @property
    def work_dir(self) -> Filepath:
        """

        Returns
        -------
        __work_dir : Filepath
            Working directory declared by this WORKDIR Instruction.
        """
        return self.__work_dir

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_work_dir = repr(self.__work_dir)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_work_dir, repr_line_num, repr_raw_code)


class ARGInstruction(Instruction):
    """
    A node of ARG Instruction.

    Attributes
    ----------
    __variable : BuildTimeVariable
        Build-time variable declared by this ARG Instruction.
    """
    __REPR_FORMAT: str = "{0}(variable={1}, line_num={2}, raw_code={3})"

    def __init__(self, variable: BuildTimeVariable, line_num: int, raw_code: str):
        """
        Parameters
        ----------
        variable : BuildTimeVariable
            Build-time variable declared by this ARG Instruction.
        line_num : int
            Line number of this ARG Instruction.
        raw_code : src
            Original Dockerfile source code.
        """
        super(ARGInstruction, self).__init__(line_num, raw_code)
        self.__variable: BuildTimeVariable = variable

    @property
    def variable(self) -> BuildTimeVariable:
        """
        Returns
        -------
        __variable : BuildTimeVariable
            Build-time variable declared by this ARG Instruction.
        """
        return self.__variable

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_variable = repr(self.__variable)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_variable, repr_line_num, repr_raw_code)


class ONBUILDInstruction(Instruction):
    """
    A node of ONBUILD Instruction.

    Attributes
    ----------
    __param_instructions : List[Instruction]
        Dockerfile Instructions as parameters of ONBUILD Instruction.
    """
    __REPR_FORMAT: str = "{0}(param_instructions={1}, line_num={2}, raw_code={3})"

    def __init__(self, param_instructions: List[Instruction], line_num: int, raw_code: str):
        """
        Parameters
        ----------
        param_instructions : List[Instruction]
            Dockerfile Instructions as parameters of ONBUILD Instruction.
        line_num : int
            Line number of this ONBUILD Instruction.
        raw_code : src
            Original Dockerfile source code.
        """
        super(ONBUILDInstruction, self).__init__(line_num, raw_code)
        self.__param_instructions: List[Instruction] = param_instructions

    @property
    def param_instructions(self) -> List[Instruction]:
        """
        Returns
        -------
        __param_instructions : List[Instruction]
            Dockerfile Instructions as parameters of ONBUILD Instruction.
        """
        return self.__param_instructions

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_param_instructions = repr(self.__param_instructions)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_param_instructions, repr_line_num, repr_raw_code)


class STOPSIGNALInstruction(Instruction):
    """
    A node of STOPSIGNAL Instruction.

    Attributes
    ----------
    __signal : SystemCallSignal
        System call signal declared by this STOPSIGNAL Instruction.
    """
    __REPR_FORMAT: str = "{0}(signal={1}, line_num={2}, raw_code={3})"

    def __init__(self, signal: SystemCallSignal, line_num: int, raw_code: str):
        """
        Parameters
        ----------
        signal : SystemCallSignal
            System call signal declared by this STOPSIGNAL Instruction.
        line_num : int
            Line number of this STOPSIGNAL Instruction.
        raw_code : str
            Original Dockerfile source code.
        """
        super(STOPSIGNALInstruction, self).__init__(line_num, raw_code)
        self.__signal: SystemCallSignal = signal

    @property
    def signal(self) -> SystemCallSignal:
        """
        Returns
        -------
        __signal : SystemCallSignal
            System call signal declared by this STOPSIGNAL Instruction.
        """
        return self.__signal

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_signal = repr(self.__signal)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_signal, repr_line_num, repr_raw_code)

    def __str__(self):
        return self.raw_code


class HEALTHCHECKInstruction(Instruction):
    """
    A node of HEALTHCHECK Instruction.

    Todo: Need to implement parse options
        * --interval=DURATION (default: 30s)
        * --timeout=DURATION (default: 30s)
        * --start-period=DURATION (default: 0s)
        * --retries=N (default: 3)

    Attributes
    ----------
    __param_instructions : List[Instruction]
        Dockerfile Instructions as parameters of HEALTHCHECK Instruction.
        HEALTHCHECK Instruction has only CMD Instruction or "NONE."
    """
    __REPR_FORMAT: str = "{0}(param_instructions={1}, line_num={2}, raw_code={3})"

    def __init__(self, param_instructions: List[Instruction], line_num: int, raw_code: str):
        """
        Parameters
        ----------
        param_instructions : List[Instruction]
            Dockerfile Instructions as parameters of HEALTHCHECK Instruction.
            HEALTHCHECK Instruction has only CMD Instruction or "NONE."
        line_num : int
            Line number of this HEALTHCHECK Instruction.
        raw_code : str
            Original Dockerfile source code.
        """
        super(HEALTHCHECKInstruction, self).__init__(line_num, raw_code)
        self.__param_instructions: List[Instruction] = param_instructions

    @property
    def param_instructions(self) -> List[Instruction]:
        """
        Returns
        -------
        __param_instructions : List[Instruction]
            Dockerfile Instructions as parameters of HEALTHCHECK Instruction.
        """
        return self.__param_instructions

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_param_instructions = repr(self.__param_instructions)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_param_instructions, repr_line_num, repr_raw_code)


class SHELLInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(SHELLInstruction, self).__init__(line_num, raw_code)

    """
    SHELL ["executable", "parameters"]
    """
