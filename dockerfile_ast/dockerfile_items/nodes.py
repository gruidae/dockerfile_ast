from abc import ABCMeta

from dockerfile_ast.dockerfile_items.bash_items.nodes import BashValueNode

from dockerfile_ast.utils import DockerfileASTNode


class DockerfileSyntaxNode(DockerfileASTNode, metaclass=ABCMeta):
    """
    A node of Dockerfile Syntax.
    """


class DockerImage(DockerfileSyntaxNode):
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


class DockerPort(DockerfileSyntaxNode):
    """
    A node of Docker port.

    Attributes
    ----------
    __port_num : BashValueNode
        Port number of this port.
    __protocol : BashValueNode
        Ethernet protocol of this port.
    """
    __REPR_FORMAT: str = "{0}(port_num={1}, protocol={2})"

    def __init__(self, port_num: BashValueNode, protocol: BashValueNode = None):
        super(DockerPort, self).__init__()
        self.__port_num: BashValueNode = port_num
        self.__protocol: BashValueNode = protocol

    @property
    def port_num(self) -> BashValueNode:
        """
        Returns
        -------
        __port_num : BashValueNode
            Port number of this port.
        """
        return self.__port_num

    @property
    def protocol(self) -> BashValueNode:
        """
        Returns
        -------
        __protocol : BashValueNode
            Ethernet protocol of this port.
        """
        return self.__protocol

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_port_num = repr(self.__port_num)
        repr_protocol = repr(self.__protocol)
        return self.__REPR_FORMAT.format(self_class_name, repr_port_num, repr_protocol)

    def __str__(self):
        if self.__protocol is None:
            return str(self.__port_num)
        else:
            return "/".join([str(self.__port_num), str(self.__protocol)])


class DockerLabel(DockerfileSyntaxNode):
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
    def name(self) -> str:
        """
        Returns
        -------
        __name : str
            This Docker label name.
        """
        return self.__name

    @property
    def value(self) -> BashValueNode:
        """

        Returns
        -------
        __value : str
            Value of this Docker label.
        """
        return self.__value

    def __repr__(self):
        self_class_name = self.__class__.__name__
        repr_name = repr(self.__name)
        repr_value = repr(self.__value)
        return self.__REPR_FORMAT.format(self_class_name, repr_name, repr_value)

    def __str__(self):
        return "=\"".join([self.name, str(self.__value)]) + "\""
