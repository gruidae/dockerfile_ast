from typing import List


class BashNode:
    __REPR_FORMAT: str = "{0}()"

    def __init__(self):
        pass

    def __repr__(self):
        self_class_name = self.__class__.__name__
        return self.__REPR_FORMAT.format(self_class_name)

    def __str__(self):
        self_class_name = self.__class__.__name__
        return self.__REPR_FORMAT.format(self_class_name)


# TODO: Bashコマンド，Bashオプションの作成．


class BashValueNode(BashNode):
    def __init__(self):
        super(BashValueNode, self).__init__()
        pass


class BashConstant(BashValueNode):
    __REPR_FORMAT: str = "{0}(value={1})"

    def __init__(self, value: str):
        super(BashConstant, self).__init__()
        self.__value = value

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_value)

    def __str__(self):
        return self.__value


class BashVariable(BashValueNode):
    __REPR_FORMAT: str = "{0}(name={1})"
    __REFERRED_NAME_FORMAT = "${{{0}}}"

    def __init__(self, name: str):
        super(BashVariable, self).__init__()
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    def referred_name(self) -> str:
        return self.__REFERRED_NAME_FORMAT.format(self.__name)

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_name = repr(self.__name)
        return self.__REPR_FORMAT.format(self_class_name, repr_name)

    def __str__(self):
        self_class_name = self.__class__.__name__
        repr_name = repr(self.__name)
        return self.__REPR_FORMAT.format(self_class_name, repr_name)


class TemporaryVariable(BashVariable):
    def __init__(self, name: str):
        super(TemporaryVariable, self).__init__(name)


class EnvironmentVariable(BashVariable):
    def __init__(self, name: str):
        super(EnvironmentVariable, self).__init__(name)


class BashConcat(BashValueNode):
    __REPR_FORMAT: str = "{0}(values={1})"

    def __init__(self, values: List[BashValueNode]):
        super(BashConcat, self).__init__()
        self.__values = values

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_values = repr(self.__values)
        return self.__REPR_FORMAT.format(self_class_name, repr_values)

    def __str__(self):
        retval: str = ""
        for value in self.__values:
            if isinstance(value, BashVariable):
                retval += value.referred_name()
            elif isinstance(value, BashConstant):
                retval += value.value
        return retval


class FilePath(BashNode):
    __REPR_FORMAT: str = "{0}(value={1})"

    def __init__(self, value: BashValueNode):
        super(FilePath, self).__init__()
        self.__value = value

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_value)

    def __str__(self):
        return str(self.__value)

# TODO: ユーザ名（ID），グループ名（ID），signalの作成．
