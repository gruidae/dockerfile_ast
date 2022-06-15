from typing import List

from .shell_items.nodes import BashValueNode


class DockerfileNode:
    def __init__(self):
        pass


class Instruction(DockerfileNode):
    __REPR_FORMAT: str = "{0}(line_num={1}, raw_code={2})"

    def __init__(self, line_num: int, raw_code: str):
        super(Instruction, self).__init__()
        self.__line_num = line_num
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

    """
    FROM [--platform=<platform>] <image> [AS <name>]
    FROM [--platform=<platform>] <image>[:<tag>] [AS <name>]
    FROM [--platform=<platform>] <image>[@<digest>] [AS <name>]
    """


class RUNInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(RUNInstruction, self).__init__(line_num, raw_code)

    """
    RUN <command>
    RUN ["executable", "param1", "param2"]
    """


class CMDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(CMDInstruction, self).__init__(line_num, raw_code)

    """
    CMD ["executable","param1","param2"]
    CMD ["param1","param2"]
    CMD command param1 param2
    """


class LABELInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(LABELInstruction, self).__init__(line_num, raw_code)

    """
    LABEL <key>=<value> <key>=<value> <key>=<value> ...
    MAINTAINER <name>
    """


class EXPOSEInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(EXPOSEInstruction, self).__init__(line_num, raw_code)

    """
    EXPOSE <port> [<port>/<protocol>...]
    """


class ENVInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(ENVInstruction, self).__init__(line_num, raw_code)

    """
    ENV <key>=<value> ...
    """


class ADDInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(ADDInstruction, self).__init__(line_num, raw_code)

    """
    ADD [--chown=<user>:<group>] <src>... <dest>
    ADD [--chown=<user>:<group>] ["<src>",... "<dest>"]
    """


class COPYInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(COPYInstruction, self).__init__(line_num, raw_code)

    """
    COPY [--chown=<user>:<group>] <src>... <dest>
    COPY [--chown=<user>:<group>] ["<src>",... "<dest>"]
    """


class ENTRYPOINTInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(ENTRYPOINTInstruction, self).__init__(line_num, raw_code)

    """
    ENTRYPOINT ["executable", "param1", "param2"]
    ENTRYPOINT command param1 param2
    """


class VOLUMEInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(VOLUMEInstruction, self).__init__(line_num, raw_code)

    """
    VOLUME ["/data"]
    """


class USERInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(USERInstruction, self).__init__(line_num, raw_code)

    """
    USER <user>[:<group>]
    USER <UID>[:<GID>]
    """


class WORKDIRInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(WORKDIRInstruction, self).__init__(line_num, raw_code)

    """
    WORKDIR /path/to/workdir
    """


class ARGInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(ARGInstruction, self).__init__(line_num, raw_code)

    """
    ARG <name>[=<default value>]
    """


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

    """
    STOPSIGNAL signal
    """


class HEALTHCHECKInstruction(Instruction):
    def __init__(self, param_instructions: List[Instruction], line_num: int, raw_code: str):
        super(HEALTHCHECKInstruction, self).__init__(line_num, raw_code)
        self.__param_instructions: List[Instruction] = param_instructions

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_param_instructions = repr(self.__param_instructions)
        repr_line_num = repr(self.line_num)
        repr_raw_code = repr(self.raw_code)
        return self.__REPR_FORMAT.format(self_class_name, repr_param_instructions, repr_line_num, repr_raw_code)


class SHELLInstruction(Instruction):
    def __init__(self, line_num: int, raw_code: str):
        super(SHELLInstruction, self).__init__(line_num, raw_code)

    """
    SHELL ["executable", "parameters"]
    """


class DockerImage(DockerfileNode):
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
    def __init__(self, port: BashValueNode, protocol: BashValueNode = None):
        super(DockerPort, self).__init__()
        self.__port: BashValueNode = port
        self.__protocol: BashValueNode = protocol


class DockerLabel(DockerfileNode):
    def __init__(self, name: str, value: BashValueNode):
        super(DockerLabel, self).__init__()
        self.__name: str = name
        self.__label = value

    @property
    def name(self):
        return self.__name
