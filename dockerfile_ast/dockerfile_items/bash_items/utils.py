from typing import Dict

from dockerfile_ast.dockerfile_items.bash_items.nodes import BashConstant
from dockerfile_ast.dockerfile_items.bash_items.nodes import EnvironmentVariable


_DEFAULT_ENVIRONMENT_VARIABLES: Dict[str, EnvironmentVariable] = {
    "HOME": EnvironmentVariable("HOME", BashConstant("~")),
    "PATH": EnvironmentVariable("PATH", BashConstant("/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")),
    "SHLVL": EnvironmentVariable("SHLVL", BashConstant("1")),
    "TERM": EnvironmentVariable("TERM", BashConstant("XTERM"))
}


def init_environment_variables():
    """
    Initialize associate array of default environment variables on a Docker image.

    Returns
    -------
    _COPIED_DEFAULT_ENVIRONMENT_VARIABLES : Dict[str, EnvironmentVariable]
        Associate array of default environment variables on a Docker image.
    """
    return _DEFAULT_ENVIRONMENT_VARIABLES.copy()
