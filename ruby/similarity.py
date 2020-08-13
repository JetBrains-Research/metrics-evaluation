from typing import Optional

import editdistance
import zss

from ruby.util import split_into_tokens, create_ast, get_ast_children, get_ast_node_label, \
    ast_labels_distance, get_ast_size


def string_similarity(sample: str, reference: str) -> float:
    sample_tokens = split_into_tokens(sample)
    reference_tokens = split_into_tokens(reference)
    sample_len = len(sample_tokens)
    reference_len = len(reference_tokens)
    if sample_len == 0 and reference_len == 0:
        return 1.
    distance = editdistance.eval(sample_tokens, reference_tokens) / max(sample_len, reference_len)
    return 1. - distance


def tree_similarity(sample: str, reference: str) -> Optional[float]:
    sample_tree = create_ast(sample)
    if sample_tree is None:
        return None

    reference_tree = create_ast(reference)
    if reference_tree is None:
        return None

    tree_edit_distance = zss.simple_distance(
        sample_tree, reference_tree,
        get_children=get_ast_children,
        get_label=get_ast_node_label,
        label_dist=ast_labels_distance
    )

    sample_size = get_ast_size(sample_tree)
    reference_size = get_ast_size(reference_tree)

    return 1. - tree_edit_distance / (sample_size + reference_size)


def ruby(sample: str, reference: str) -> float:
    tree_sim = tree_similarity(sample, reference)
    if tree_sim is not None:
        return tree_sim
    return string_similarity(sample, reference)
