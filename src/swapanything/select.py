from typing import Iterable, Optional

import networkx as nx
import numpy as np
import pandas as pd

from .backend import BackendType


def select_matches(
    matches: pd.DataFrame,
    backend: BackendType,
    match_scores: Optional[pd.Series] = None,
    maxcardinality: Optional[bool] = None,
) -> pd.DataFrame:
    assert matches[backend.availability_subject_column].is_unique

    _matches = matches[backend.availability_subject_column].apply(pd.Series)
    _matches.columns = ("s1", "s2")
    if isinstance(match_scores, Iterable):
        _matches["score"] = np.array(match_scores)
        maxcardinality = maxcardinality or False
    else:
        _matches["score"] = 1
        maxcardinality = True

    G = nx.from_pandas_edgelist(_matches, "s1", "s2", ["score"])
    results_weighted = nx.algorithms.matching.max_weight_matching(
        G, maxcardinality=maxcardinality, weight="score"
    )
    results_weighted = pd.Index(
        {tuple(sorted(x)) for x in results_weighted},
        tupleize_cols=False,
        name=backend.availability_subject_column,
    )

    selected = (
        matches.set_index(backend.availability_subject_column)
        .reindex(pd.Index(results_weighted, tupleize_cols=False))
        .sort_index()
        .reset_index()
    )

    return selected
