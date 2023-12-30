from typing import Iterable, Optional

import networkx as nx
import numpy as np
import pandas as pd


def select_matches(
    matches: pd.DataFrame,
    subjects_col: str,
    slots_col: str,
    match_scores: Optional[pd.Series] = None,
    maxcardinality: Optional[bool] = None,
    return_graph: bool = False,
) -> pd.DataFrame:
    assert matches[subjects_col].is_unique

    _matches = matches[subjects_col].apply(pd.Series)
    _matches.columns = ("_s1", "_s2")
    _matches[slots_col] = matches[slots_col]
    if isinstance(match_scores, Iterable):
        _matches["_score"] = np.array(match_scores)
        maxcardinality = maxcardinality or False
    else:
        _matches["_score"] = 1
        maxcardinality = True

    G = nx.from_pandas_edgelist(_matches, "_s1", "_s2", ["_score", slots_col])
    results_weighted = nx.algorithms.matching.max_weight_matching(
        G, maxcardinality=maxcardinality, weight="_score"
    )
    results_weighted = pd.Index(
        {tuple(sorted(x)) for x in results_weighted},
        tupleize_cols=False,
        name=subjects_col,
    )

    selected = (
        matches.set_index(subjects_col)
        .reindex(pd.Index(results_weighted, tupleize_cols=False))
        .sort_index()
        .reset_index()
    )

    if return_graph:
        return selected, G
    else:
        return selected
