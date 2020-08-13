import tokenize
import ast

from io import BytesIO
from typing import List, Optional, Union, Any


def split_into_tokens(code: str) -> List[str]:
    try:
        tokens = list(tokenize.tokenize(BytesIO(code.encode('utf-8')).readline))[1:]
        tokens = [token.string for token in tokens]
    except tokenize.TokenError:
        tokens = code.split()
    return tokens


def create_ast(code: str) -> Optional[ast.AST]:
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def get_ast_children(node: Union[Any, ast.AST]) -> List[Union[Any, ast.AST]]:
    if not isinstance(node, ast.AST):
        return []

    def wrap(node_field: Union[list, Union[Any, ast.AST]]) -> List[Union[Any, ast.AST]]:
        if isinstance(node_field, list):
            return node_field
        return [node_field]

    children = [
        child
        for field in node._fields
        for child in wrap(getattr(node, field))
    ]
    return children


def get_ast_node_label(node: Union[Any, ast.AST]) -> str:
    if not isinstance(node, ast.AST):
        return str(node)
    return str(type(node))


def ast_labels_distance(label1: str, label2: str) -> float:
    if label1 == label2:
        return 0.
    return 1.


def get_ast_size(node: Union[str, ast.AST]) -> int:
    if isinstance(node, int):
        return 1
    return sum(1 for _ in ast.walk(node))
