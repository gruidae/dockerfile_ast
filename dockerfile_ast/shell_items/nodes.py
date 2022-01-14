from typing import List


class BashValueNode:
    pass


class BashConstant(BashValueNode):
    def __init__(self, value: str):
        self.__value = value


class BashVariable(BashValueNode):
    def __init__(self, name: str):
        self.__name = name

    @property
    def name(self):
        return self.__name


class TemporaryVariable(BashVariable):
    def __init__(self, name: str):
        super(TemporaryVariable, self).__init__(name)


class EnvironmentVariable(BashVariable):
    def __init__(self, name: str):
        super(EnvironmentVariable, self).__init__(name)


class BashConcat(BashValueNode):
    def __init__(self, values: List):
        self.__value = values


class FilePath:
    def __init__(self, value):
        self.__value = value
