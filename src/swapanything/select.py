from typing import Iterable, Optional

import networkx as nx
import numpy as np
import pandas as pd

"""
Select matches module. In this module you'll find everything related to the selection
of matches between individuals. This means you'll obtain a subset of the found matches among
all the feasible ones.
"""

def select_matches(
    matches: pd.DataFrame,
    subjects_col: str,
    slots_col: str,
    match_scores: Optional[pd.Series] = None,
    maxcardinality: Optional[bool] = None,
    return_graph: bool = False,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    matches: pandas.DataFrame
             Dataframe containing the matches to be selected. The df is expected to have a column containing the time slots and
             a column couples of subjects. Each time slot has a unique couple assigned to it.
    subjects_col: str
                  Name of the column where subjects, namely individuals, are stored. The subjects are
                  expected to be unique.
    slots_col: str
               Name of the column where time slots indicating subjects availabilities are stored.
    match_scores: pandas.Series, default=None
                  Score defining the affinity of a match between individuals, higher score defines higher affinity.
                  Matching algorithm tries to maximize the weight of the selected edges.
    maxcardinality: bool, default=None
                    If maxcardinality is True, compute the maximum-cardinality matching with maximum
                    weight among all maximum-cardinality matchings.
    return_graph: bool, default=False
                  If True the function returns the graph obtained from the matches between individuals other than the
                  selected matches.

    Returns
    -------
    selected: pandas.DataFrame
    G: networkx.Graph, optional

    Raises
    ------
    AssertionError
        If the subjects in the matches table are not unique

    Examples
    --------
    all_possible_matches = be.get_all_matches()
    |   |                 subject |   availability |
    ------------------------------------------------
    | 0 |   (Barbarianna, Katana) |       (12:00,) |
    | 1 |   (Hackerman, KungFury) |       (10:00,) |
    | 2 | (Hackerman, Triceracop) |       (11:00,) |
    | 3 |      (Hoff 9000, T-Rex) |       (16:00,) |
    | 4 |        (KungFury, Thor) | (13:00, 14:00) |
    | 5 |  (KungFury, Triceracop) |        (9:00,) |
    | 6 |           (T-Rex, Thor) |       (15:00,) |

    select_matches(all_possible_matches, backend=be)
    |   |                 subject |   availability |
    ------------------------------------------------
    | 0 |   (Barbarianna, Katana) |       (12:00,) |
    | 1 | (Hackerman, Triceracop) |       (11:00,) |
    | 2 |      (Hoff 9000, T-Rex) |       (16:00,) |
    | 3 |        (KungFury, Thor) | (13:00, 14:00) |
    """
    assert matches[subjects_col].is_unique

    # Considering the table entry 9:00 (KungFury, Triceracop), we expand the subject couple to obtain the following dataframe:
    # _matches: _s1     | _s2
    #           KungFury| Triceracop
    _matches = matches[subjects_col].apply(pd.Series)
    _matches.columns = ("_s1", "_s2")
    _matches[slots_col] = matches[slots_col]
    if isinstance(match_scores, Iterable):
        _matches["_score"] = np.array(match_scores)
        maxcardinality = maxcardinality or False
    else:
        _matches["_score"] = 1
        maxcardinality = True

    G: nx.Graph = nx.from_pandas_edgelist(
        df=_matches, source="_s1", target="_s2", edge_attr=["_score", slots_col]
        )
    results_weighted: set = nx.algorithms.matching.max_weight_matching(
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
