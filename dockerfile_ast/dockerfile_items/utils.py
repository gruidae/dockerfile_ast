from enum import Enum


class InstructionEnum(Enum):
    """
    Enumerated Dockerfile Instructions.
    """
    ADD = "ADD"
    ARG = "ARG"
    CMD = "CMD"
    COPY = "COPY"
    ENTRYPOINT = "ENTRYPOINT"
    ENV = "ENV"
    EXPOSE = "EXPOSE"
    FROM = "FROM"
    HEALTHCHECK = "HEALTHCHECK"
    LABEL = "LABEL"
    MAINTAINER = "MAINTAINER"
    ONBUILD = "ONBUILD"
    RUN = "RUN"
    SHELL = "SHELL"
    STOPSIGNAL = "STOPSIGNAL"
    USER = "USER"
    VOLUME = "VOLUME"
    WORKDIR = "WORKDIR"

    @staticmethod
    def of(instruction_name: str):
        for item in InstructionEnum:
            if item.value == instruction_name.upper():
                return item
        raise ValueError("InstructionEnum: {0} instruction is not defined.".format(instruction_name))

    def __str__(self):
        return self.value
