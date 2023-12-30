from typing import List

import networkx as nx
import pandas as pd
import pytest
from swapanything import select


@pytest.fixture
def subject_features() -> List[str]:
    return ["a", "b", "c"]


@pytest.fixture
def subjects_col() -> str:
    return "subj"


@pytest.fixture
def slots_col() -> str:
    return "avail"


@pytest.fixture
def exclusions_subject_columns() -> List[str]:
    return ["es1", "es2"]


@pytest.fixture
def possible_matches() -> List[List[tuple]]:
    possible_matches = [
        [("sub1", "sub2"), ("A",)],
        [("sub1", "sub3"), ("B",)],
        [("sub2", "sub3"), ("C",)],
        [("sub4", "sub5"), ("D",)],
        [("sub1", "sub6"), ("E", "F")],
        [("sub6", "sub7"), ("G",)],
        [("sub7", "sub8"), ("H",)],
    ]
    return possible_matches


@pytest.mark.parametrize(
    "scores,expected_result_ixs",
    [
        (
            None,
            [4, 2, 3, 6],
            # [("sub1", "sub6"), ("E", "F")],
            # [("sub2", "sub3"), ("C",)],
            # [("sub4", "sub5"), ("D",)],
            # [("sub7", "sub8"), ("H",)],
        ),
        (
            # to test mismatching index
            pd.Series([1.0, 1.0, 1.0, 1.0, 1.0, 9001.0, 1.0]),
            [0, 3, 5]
            # [("sub1", "sub2"), ("A",)],
            # [("sub4", "sub5"), ("D",)],
            # [("sub6", "sub7"), ("G",)],
        ),
        ([1.0, 1.0, 1.0, 1.0, 1.0, 9001.0, 1.0], [0, 3, 5]),
    ],
)
def test_select_matches(
    scores,
    expected_result_ixs,
    subjects_col: str,
    slots_col: str,
    possible_matches: List[List[tuple]],
) -> None:
    matches = pd.DataFrame(
        possible_matches,
        columns=[
            subjects_col,
            slots_col,
        ],
        index=[0] * 7,
    )

    results = select.select_matches(
        matches,
        subjects_col=subjects_col,
        slots_col=slots_col,
        match_scores=scores,
    )

    expected_result = matches.iloc[expected_result_ixs].reset_index(drop=True)
    assert isinstance(results, pd.DataFrame)
    assert results.columns[0] == subjects_col
    assert results.columns[1] == slots_col
    assert results.equals(expected_result)

    _, G = select.select_matches(
        matches,
        subjects_col=subjects_col,
        slots_col=slots_col,
        match_scores=scores,
        return_graph=True,
    )
    assert isinstance(G, nx.Graph)
