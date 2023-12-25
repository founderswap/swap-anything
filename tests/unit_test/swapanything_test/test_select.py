from copy import deepcopy

import pandas as pd
import pytest
from swapanything import select
from swapanything.backend import _base


@pytest.fixture
def subject_features() -> list[str]:
    return ["a", "b", "c"]


@pytest.fixture
def availability_subject_column() -> str:
    return "subj"


@pytest.fixture
def availabilities_column() -> str:
    return "avail"


@pytest.fixture
def exclusions_subject_columns() -> list[str]:
    return ["es1", "es2"]


@pytest.fixture
def dummy_backend(
    subject_features: list[str],
    availability_subject_column: str,
    availabilities_column: str,
    exclusions_subject_columns: list[str],
) -> _base.BackendType:
    class TestBackend(_base.BackendBase):
        def __init__(self) -> None:
            self.subject_features = subject_features
            self.availability_subject_column = availability_subject_column
            self.availabilities_column = availabilities_column
            self.exclusions_subject_columns = exclusions_subject_columns

        def get_subjects(self) -> None:
            raise NotImplementedError()

        def get_availabilities(self) -> pd.DataFrame:
            raise NotImplementedError()

        def get_exclusions(self) -> pd.DataFrame:
            raise NotImplementedError()

    return TestBackend()


_M = [
    [("sub1", "sub2"), ("A",)],
    [("sub1", "sub3"), ("B",)],
    [("sub2", "sub3"), ("C",)],
    [("sub4", "sub5"), ("D",)],
    [("sub1", "sub6"), ("E", "F")],
    [("sub6", "sub7"), ("G",)],
    [("sub7", "sub8"), ("H",)],
]


@pytest.fixture
def possible_matchings() -> list[list[tuple]]:
    return deepcopy(_M)


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
    possible_matchings: list[list[tuple]],
    dummy_backend: _base.BackendType,
) -> None:
    matches = pd.DataFrame(
        possible_matchings,
        columns=[
            dummy_backend.availability_subject_column,
            dummy_backend.availabilities_column,
        ],
        index=[0] * 7,
    )

    results = select.select_matches(
        matches,
        backend=dummy_backend,
        match_scores=scores,
    )

    expected_result = matches.iloc[expected_result_ixs].reset_index(drop=True)
    assert isinstance(results, pd.DataFrame)
    assert results.columns[0] == dummy_backend.availability_subject_column
    assert results.columns[1] == dummy_backend.availabilities_column
    assert results.equals(expected_result)
