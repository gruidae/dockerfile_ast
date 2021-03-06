from abc import ABCMeta
from typing import List

from dockerfile_ast.utils import DockerfileASTNode


class BashNode(DockerfileASTNode, metaclass=ABCMeta):
    """
    A node of Bash Syntax.
    """


class BashValueNode(BashNode, metaclass=ABCMeta):
    """
    A node of Bash value such as variables or constants.
    """


class BashConstant(BashValueNode):
    """
    A node of Bash constant.

    Attributes
    ----------
    __value : str
        Value of this constant.
    """
    __REPR_FORMAT: str = "{0}(value={1})"

    def __init__(self, value: str):
        """
        Parameters
        ----------
        value : str
            Value of this constant.
        """
        super(BashConstant, self).__init__()
        self.__value = value

    @property
    def value(self) -> str:
        """
        Returns
        -------
        __value : str
            Value of this constant.
        """
        return self.__value

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_value)

    # override
    def __str__(self):
        return self.__value


class BashVariable(BashValueNode):
    """
    A node of Bash variable.

    Attributes
    ----------
    __name : str
        Name of this variable.
    """
    __REPR_FORMAT: str = "{0}(name={1})"
    __REFERRED_NAME_FORMAT = "${{{0}}}"

    def __init__(self, name: str):
        """
        Parameters
        ----------
        name : str
            Name of this variable.
        """
        super(BashVariable, self).__init__()
        self.__name = name

    @property
    def name(self) -> str:
        """
        Returns
        -------
        __name : str
            Name of this variable.
        """
        return self.__name

    def referenced_name(self) -> str:
        """
        Return this variable name when referenced in Dockerfile such as `${FOO}`.

        Returns
        -------
        referenced_name : str
            Variable name when referenced in Dockerfile.
        """
        return self.__REFERRED_NAME_FORMAT.format(self.__name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if self is other:
            return True
        elif other is None:
            return False
        elif not isinstance(other, BashVariable):
            return False
        else:
            return self.__name == other.__name

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_name = repr(self.__name)
        return self.__REPR_FORMAT.format(self_class_name, repr_name)

    # override
    def __str__(self):
        return self.__name


class BuildTimeVariable(BashVariable):
    """
    A node of build-time variable (ARG Variable of Dockerfile).

    Attributes
    ----------
    __value : BashValueNode
        Value of this temporary variable.
    """
    __REPR_FORMAT: str = "{0}(name={1}, value={2})"

    def __init__(self, name: str, value: BashValueNode):
        """

        Parameters
        ----------
        name : str
            Name of this build-time variable.
        value : BashValueNode
            Value of this build-time variable.
        """
        super(BuildTimeVariable, self).__init__(name)
        self.__value: BashValueNode = value

    @property
    def value(self) -> BashValueNode:
        """
        Returns
        -------
        __value : BashValueNode
            Value of this build-time variable.
        """
        return self.__value

    # override
    def __eq__(self, other):
        if self is other:
            return True
        elif other is None:
            return False
        elif not isinstance(other, BuildTimeVariable):
            return False
        else:
            return self.__name == other.__name

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_name = repr(self.name)
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_name, repr_value)

    # override
    def __str__(self):
        if self.__value is None:
            return super(BuildTimeVariable, self).__str__()
        else:
            return "=".join([self.name, str(self.__value)])


class EnvironmentVariable(BashVariable):
    """
    A node of EnvironmentVariable (ENV Variable of Dockerfile).

    Attributes
    ----------
    __value : BashValueNode
        Value of this environment variable.
    """
    __REPR_FORMAT: str = "{0}(name={1}, value={2})"

    def __init__(self, name: str, value: BashValueNode):
        """
        Parameters
        ----------
        name : str
            Name of this environment variable.
        value : BashValueNode
            Value of this environment variable.
        """
        super(EnvironmentVariable, self).__init__(name)
        self.__value: BashValueNode = value

    @property
    def value(self) -> BashValueNode:
        """
        Returns
        -------
        __value : BashValueNode
            Value of this environment variable.
        """
        return self.__value

    # override
    def __eq__(self, other):
        if self is other:
            return True
        elif other is None:
            return False
        elif not isinstance(other, BuildTimeVariable):
            return False
        else:
            return self.__name == other.__name

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_name = repr(self.name)
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_name, repr_value)

    # override
    def __str__(self):
        return "=".join([self.name, str(self.__value)])


class BashConcat(BashValueNode):
    """
    A node of Bash concat, which has both Bash variables and Bash constants.

    Attributes
    ----------
    __values : List[BashValueNode]
        Nodes of Bash variables and Bash constants.
    """
    __REPR_FORMAT: str = "{0}(values={1})"

    def __init__(self, values: List[BashValueNode]):
        """
        Parameters
        ----------
        values : List[BashValueNode]
            Nodes of Bash variables and Bash constants.
        """
        super(BashConcat, self).__init__()
        self.__values = values

    @property
    def values(self) -> List[BashValueNode]:
        """
        Returns
        -------
        __values : List[BashValueNode]
            Nodes of Bash variables and Bash constants.
        """
        return self.__values

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_values = repr(self.__values)
        return self.__REPR_FORMAT.format(self_class_name, repr_values)

    # override
    def __str__(self):
        retval: str = ""
        for value in self.__values:
            if isinstance(value, BashVariable):
                retval += value.referenced_name()
            elif isinstance(value, BashConstant):
                retval += value.value
        return retval

# TODO: Bash???????????????Bash?????????????????????????????????ID????????????????????????ID???


class Filepath(BashNode):
    """
    A node of filepath on Docker container.

    Attributes
    ---------
    __value : BashValueNode
        Concrete filepath on this Dockerfile.
    """
    __REPR_FORMAT: str = "{0}(value={1})"

    def __init__(self, value: BashValueNode):
        """
        Parameters
        ----------
        value : BashValueNode
            Concrete filepath on this Dockerfile.
        """
        super(Filepath, self).__init__()
        self.__value = value

    @property
    def value(self) -> BashValueNode:
        """
        Returns
        -------
        __value : BashValueNode
            Concrete filepath on this Dockerfile.
        """
        return self.__value

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_value)

    # override
    def __str__(self):
        return str(self.__value)


class SystemCallSignal(BashNode):
    """
    A node of system call signal that will be sent to the container to exit.

    Attributes
    ----------
    __value : BashValueNode
        Concrete system call signal.
    """
    __REPR_FORMAT: str = "{0}(value={1})"

    def __init__(self, value: BashValueNode):
        """
        Parameters
        ----------
        value : BashValueNode
            Concrete system call signal.
        """
        super(SystemCallSignal, self).__init__()
        self.__value: BashValueNode = value

    @property
    def value(self) -> BashValueNode:
        """
        Returns
        -------
        __value : BashValueNode
            Concrete system call signal.
        """
        return self.__value

    # override
    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_value)

    def __str__(self):
        return str(self.__value)
