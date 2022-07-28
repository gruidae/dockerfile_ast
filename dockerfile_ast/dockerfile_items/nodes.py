from abc import ABCMeta

from dockerfile_ast.dockerfile_items.bash_items.nodes import BashValueNode

from dockerfile_ast.utils import DockerfileASTNode


class DockerfileSyntaxNode(DockerfileASTNode, metaclass=ABCMeta):
    """
    A node of Dockerfile Syntax.
    """
    def __init__(self):
        pass


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
        return "=\"".join([self.name, str(self.__value)]) + "\""
