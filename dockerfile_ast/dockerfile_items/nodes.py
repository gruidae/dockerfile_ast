from abc import ABCMeta
from typing import List

from .bash_items.nodes import BashValueNode
from .bash_items.nodes import EnvironmentVariable
from .bash_items.nodes import TemporaryVariable


class DockerfileNode(metaclass=ABCMeta):
    """
    A node of Dockerfile Syntax.
    """

    def __init__(self):
        pass


class DockerImage(DockerfileNode):
    # TODO: Need to implement
    def __init__(
            self,
            name: BashValueNode,
            tag: BashValueNode = None,
            digest: BashValueNode = None,
            as_name: BashValueNode = None
    ):
        super(DockerImage, self).__init__()
        self.__name = name
        self.__tag = tag
        self.__digest = digest
        self.__as_name = as_name


class DockerPort(DockerfileNode):
    # TODO: Need to implement
    def __init__(self, port: BashValueNode, protocol: BashValueNode = None):
        super(DockerPort, self).__init__()
        self.__port: BashValueNode = port
        self.__protocol: BashValueNode = protocol

    @property
    def port(self):
        return self.__port

    @property
    def protocol(self):
        return self.__protocol


class DockerLabel(DockerfileNode):
    """
    A node of Docker label.

    Attributes
    ----------
    __name : str
        This Docker label name.
    --value : str
        Value of this Docker label.
    """
    MAINTAINER_NAME = "maintainer"
    __REPR_FORMAT: str = "{0}(name={1}, value={2})"

    def __init__(self, name: str, value: BashValueNode):
        """
        Parameters
        ----------
        name : str
            This Docker label name.
        value : str
            Value of this Docker label.
        """
        super(DockerLabel, self).__init__()
        self.__name: str = name
        self.__value = value

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_name = repr(self.__name)
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_name, repr_value)

    def __str__(self):
        return self.name + str(self.__value)


class Instruction(DockerfileNode, metaclass=ABCMeta):
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
    def labels(self):
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
        retval = "LABEL "
        for label in self.__labels:
            retval += label.name + "=" + str(label.value)
        return retval


class EXPOSEInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(EXPOSEInstruction, self).__init__(line_num, raw_code)

    """
    EXPOSE <port> [<port>/<protocol>...]
    """


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
    def variables(self):
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
        retval = "ENV "
        for variable in self.__variables:
            retval += variable.name + "=" + str(variable.value)
        return retval


class ADDInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(ADDInstruction, self).__init__(line_num, raw_code)

    """
    ADD [--chown=<user>:<group>] <src>... <dest>
    ADD [--chown=<user>:<group>] ["<src>",... "<dest>"]
    """


class COPYInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(COPYInstruction, self).__init__(line_num, raw_code)

    """
    COPY [--chown=<user>:<group>] <src>... <dest>
    COPY [--chown=<user>:<group>] ["<src>",... "<dest>"]
    """


class ENTRYPOINTInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(ENTRYPOINTInstruction, self).__init__(line_num, raw_code)

    """
    ENTRYPOINT ["executable", "param1", "param2"]
    ENTRYPOINT command param1 param2
    """


class VOLUMEInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(VOLUMEInstruction, self).__init__(line_num, raw_code)

    """
    VOLUME ["/data"]
    """


class USERInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(USERInstruction, self).__init__(line_num, raw_code)

    """
    USER <user>[:<group>]
    USER <UID>[:<GID>]
    """


class WORKDIRInstruction(Instruction):
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(WORKDIRInstruction, self).__init__(line_num, raw_code)

    """
    WORKDIR /path/to/workdir
    """


class ARGInstruction(Instruction):
    """
    A node of ARG Instruction.

    Attributes
    ----------
    __variable : TemporaryVariable
        Temporary variable declared by this ARG Instruction.
    """
    __REPR_FORMAT: str = "{0}(variable={1}, line_num={2}, raw_code={3})"

    def __init__(self, variable: TemporaryVariable, line_num: int, raw_code: str):
        """
        Parameters
        ----------
        variable : TemporaryVariable
            Temporary variable declared by this ARG Instruction.
        line_num : int
            Line number of this ARG Instruction.
        raw_code : src
            Original Dockerfile source code.
        """
        super(ARGInstruction, self).__init__(line_num, raw_code)
        self.__variable: TemporaryVariable = variable

    @property
    def variable(self):
        """
        Returns
        -------
        __variable : TemporaryVariable
            Temporary variable declared by this ARG Instruction.
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
    def param_instructions(self):
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
    # TODO: Need to implement
    def __init__(self, line_num: int, raw_code: str):
        super(STOPSIGNALInstruction, self).__init__(line_num, raw_code)

    """
    STOPSIGNAL signal
    """


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
    def param_instructions(self):
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
