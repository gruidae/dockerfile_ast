import bashlex
import re
from typing import Dict, List

from dockerfile_ast.dockerfile_items.bash_items.nodes import BashValueNode
from dockerfile_ast.dockerfile_items.bash_items.nodes import BashConcat
from dockerfile_ast.dockerfile_items.bash_items.nodes import BashConstant
from dockerfile_ast.dockerfile_items.bash_items.nodes import BashVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import EnvironmentVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import BuildTimeVariable


class BashParser:
    """
    A parser of Bash Syntax.
    """
    def __init__(self):
        pass

    @staticmethod
    def __simple_parse_bash_variable(
            variable_name: str,
            arg_variables: Dict[str, BuildTimeVariable],
            env_variables: Dict[str, EnvironmentVariable]
    ) -> BashVariable:
        """
        Simply parse Bash variable.

        Parameters
        ----------
        variable_name : str
            Variable name on Dockerfile.
        arg_variables : Dict[str, BuildTimeVariable]
            Associative array of build-time variable on Dockerfile.
        env_variables : Dict[str, EnvironmentVariable]
            Associative array of environment variable on Dockerfile.
        Returns
        -------
        bash_variable : BashVariable
            A node of Bash variable.
        """
        if env_variables is not None and variable_name in env_variables.keys():
            return env_variables[variable_name]
        elif arg_variables is not None and variable_name in arg_variables.keys():
            return arg_variables[variable_name]
        else:
            return BashVariable(variable_name)

    @staticmethod
    def simple_parse_bash_concat(
            token: str,
            arg_variables: Dict[str, BuildTimeVariable],
            env_variables: Dict[str, EnvironmentVariable]
    ) -> BashValueNode:
        """
        Simply parse Bash concat (Bash variables and constants).

        Parameters
        ----------
        token : str
            Token including Bash variables and constants.
        arg_variables : Dict[str, BuildTimeVariable]
            Associative array of build-time variable on Dockerfile.
        env_variables : Dict[str, EnvironmentVariable]
            Associative array of environment variable on Dockerfile.
        Returns
        -------
        bash_value_node : BashValueNode
            A node of Bash variable, constant or concat.
        """
        if token is None:
            return None
        # CommandNode()ではないため，直接WordNodeへとVisit
        bashlex_token = bashlex.parse(token)[0].parts[0]
        bashlex_variables: List = bashlex_token.parts

        if len(bashlex_variables) < 1:
            # 定数のみ
            return BashConstant(bashlex_token.word)
        elif len(bashlex_variables) == 1:
            # 変数のみ（${variable:-word}や${variable:+word}は非対応）
            variable_name = bashlex_variables[0].value
            if re.match(r"^\$(\{\w+}|\w+)$", bashlex_token.word):
                return BashParser.__simple_parse_bash_variable(variable_name, arg_variables, env_variables)

        # 変数と定数の分離
        split_tokens = [bashlex_token.word]
        for bashlex_variable in bashlex_variables:
            variable_name = bashlex_variable.value
            tmp_split_tokens1 = split_tokens
            split_tokens = list()
            for tmp_split_token1 in tmp_split_tokens1:
                if isinstance(tmp_split_token1, str):
                    # 変数名でトークンを分割
                    tmp_split_tokens2 = re.split(r"\$\{" + variable_name + r"}|\$" + variable_name, tmp_split_token1)
                    is_head_split_tokens = True
                    for tmp_split_token2 in tmp_split_tokens2:
                        tmp_split_token2 = tmp_split_token2
                        if not is_head_split_tokens:
                            # 変数はあらかじめparseしておく
                            variable: BashVariable = BashParser.__simple_parse_bash_variable(
                                variable_name, arg_variables, env_variables
                            )
                            split_tokens.append(variable)
                        if len(tmp_split_token2) > 0:
                            split_tokens.append(tmp_split_token2)
                        is_head_split_tokens = False
                else:
                    split_tokens.append(tmp_split_token1)

        nodes: List[BashValueNode] = list()
        for token in split_tokens:
            if isinstance(token, str):
                nodes.append(BashConstant(token))
            else:
                nodes.append(token)
        return BashConcat(nodes)
