import bashlex
from typing import Dict, List
import re

from dockerfile_ast.dockerfile_items.bash_items.nodes import BashValueNode
from dockerfile_ast.dockerfile_items.bash_items.nodes import BashConcat
from dockerfile_ast.dockerfile_items.bash_items.nodes import BashConstant
from dockerfile_ast.dockerfile_items.bash_items.nodes import BashVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import EnvironmentVariable
from dockerfile_ast.dockerfile_items.bash_items.nodes import TemporaryVariable


class BashParser:
    """
    A parser of Bash Syntax.
    """
    def __init__(self):
        pass

    @staticmethod
    def __simple_parse_bash_variable(
            variable_name: str,
            arg_variables: Dict[str, TemporaryVariable],
            env_variables: Dict[str, EnvironmentVariable]
    ) -> BashVariable:
        if env_variables is not None and variable_name in env_variables.keys():
            return EnvironmentVariable(variable_name)
        elif env_variables is not None and variable_name in arg_variables.keys():
            return TemporaryVariable(variable_name)
        else:
            return BashVariable(variable_name)

    @staticmethod
    def simple_parse_bash_concat(
            token: str,
            arg_variables: Dict[str, TemporaryVariable],
            env_variables: Dict[str, EnvironmentVariable]
    ) -> BashValueNode:
        if token is None:
            return None
        # CommandNode()ではないため，直接WordNodeへとVisit
        bashlex_token: bashlex.ast.node = bashlex.parse(token)[0].parts[0]
        bashlex_variables: List[bashlex.ast.node] = bashlex_token.parts

        if len(bashlex_variables) < 1:
            # 定数のみ
            return BashConstant(bashlex_token.word)
        elif len(bashlex_variables) == 1:
            # 変数のみ（${variable:-word}や${variable:+word}は非対応）
            variable_name = bashlex_variables[0].value
            if re.match(r"^\$(\{\w+\}|\w+)$", bashlex_token.word):
                return BashParser.__simple_parse_bash_variable(variable_name, arg_variables, env_variables)

        # 変数と定数が連結されているトークン
        nodes: List[BashValueNode] = list()
        split_tokens = [bashlex_token.word]
        for bashlex_variable in bashlex_variables:
            variable_name = bashlex_variable.value
            tmp_split_tokens1 = split_tokens
            split_tokens = list()
            for tmp_split_token1 in tmp_split_tokens1:
                if isinstance(tmp_split_token1, str):
                    tmp_split_tokens2 = re.split(r"\$\{" + variable_name + r"\}|\$" + variable_name, tmp_split_token1)
                    is_head_split_tokens = True
                    for tmp_split_token2 in tmp_split_tokens2:
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

        nodes = list()
        for token in split_tokens:
            if isinstance(token, str):
                nodes.append(BashConstant(token))
            else:
                nodes.append(token)
        return BashConcat(nodes)
