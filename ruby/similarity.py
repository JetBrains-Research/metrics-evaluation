from typing import Optional, List

import editdistance
import zss

from ruby.util import split_into_tokens, create_ast, get_ast_children, get_ast_node_label, \
    ast_labels_distance, get_ast_size, naive_split_into_tokens


def sequence_similarity(sample_seq: List[str], reference_seq: List[str]) -> float:
    sample_len = len(sample_seq)
    reference_len = len(reference_seq)
    if sample_len == 0 and reference_len == 0:
        return 1.
    distance = editdistance.eval(sample_seq, reference_seq) / max(sample_len, reference_len)
    return 1. - distance


def string_similarity(sample: str, reference: str) -> float:
    sample_tokens = naive_split_into_tokens(sample)
    reference_tokens = naive_split_into_tokens(reference)
    return sequence_similarity(sample_tokens, reference_tokens)


def token_similarity(sample: str, reference: str) -> Optional[float]:
    sample_tokens = split_into_tokens(sample)
    if sample_tokens is None:
        return None

    reference_tokens = split_into_tokens(reference)
    if reference_tokens is None:
        return None

    return sequence_similarity(sample_tokens, reference_tokens)


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
    token_sim = token_similarity(sample, reference)
    if token_sim is not None:
        return token_sim
    return string_similarity(sample, reference)
