from typing import Optional, Tuple

import editdistance

from ruby.nx_graphs import compute_ged, convert_ast_to_graph, convert_dict_to_graph
from ruby.util import tokenize_tranx, create_ast, create_graph


def string_similarity(sample: str, reference: str) -> float:
    sample_tokens = tokenize_tranx(sample)
    reference_tokens = tokenize_tranx(reference)
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

    tree_edit_distance, total_size = compute_ged(
        convert_ast_to_graph(sample_tree), convert_ast_to_graph(reference_tree), use_edge_cost=False
    )

    return 1. - tree_edit_distance / total_size


def graph_similarity(sample: str, reference: str) -> Optional[float]:
    sample_graph = create_graph(sample)
    if sample_graph is None:
        return None

    reference_graph = create_graph(reference)
    if reference_graph is None:
        return None

    graph_edit_distance, total_size = compute_ged(
        convert_dict_to_graph(sample_graph), convert_dict_to_graph(reference_graph), use_edge_cost=True
    )

    return 1. - graph_edit_distance / total_size


def ruby(sample: str, reference: str) -> Tuple[float, str]:
    graph_sim = graph_similarity(sample, reference)
    if graph_sim is not None:
        return graph_sim, "graph"
    tree_sim = tree_similarity(sample, reference)
    if tree_sim is not None:
        return tree_sim, "tree"
    return string_similarity(sample, reference), "string"
