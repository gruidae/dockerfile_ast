from typing import List


class BashNode:
    def __init__(self):
        pass


# TODO: Bashコマンド，Bashオプションの作成．


class BashValueNode(BashNode):
    def __init__(self):
        super(BashValueNode, self).__init__()
        pass


class BashConstant(BashValueNode):
    def __init__(self, value: str):
        super(BashConstant, self).__init__()
        self.__value = value


class BashVariable(BashValueNode):
    def __init__(self, name: str):
        super(BashVariable, self).__init__()
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


# TODO: 変数定義の作成．


class BashConcat(BashValueNode):
    def __init__(self, values: List[BashValueNode]):
        super(BashConcat, self).__init__()
        self.__value = values


class FilePath(BashNode):
    def __init__(self, value: BashValueNode):
        super(FilePath, self).__init__()
        self.__value = value


# TODO: ユーザ名（ID），グループ名（ID），signalの作成．
