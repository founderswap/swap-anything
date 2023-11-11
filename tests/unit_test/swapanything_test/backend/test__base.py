import pandas as pd
from swapanything.backend import _base


def test__get_matching_subjects_by_slot():
    AVAIL_COL = "avail"
    SUBJ_COL = "subj"
    df = pd.DataFrame(
        [
            ["sub1", "A"],
            ["sub2", "B"],
            ["sub5", "A"],
            ["sub3", "A"],
            ["sub4", "C"],
        ],
        columns=[SUBJ_COL, AVAIL_COL],
    )

    expected_result = pd.DataFrame(
        [
            ["A", ("sub1", "sub5", "sub3")],
        ],
        columns=[AVAIL_COL, SUBJ_COL],
    )

    result = _base._get_matching_subjects_by_slot(
        availabilities=df,
        availability_subject_column=SUBJ_COL,
        availabilities_column=AVAIL_COL,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.equals(expected_result)


def test__get_matches_from_slots():
    AVAIL_COL = "avail"
    SUBJ_COL = "subj"
    slots = pd.DataFrame(
        [
            ["A", ("sub1", "sub5", "sub3")],
        ],
        columns=[AVAIL_COL, SUBJ_COL],
    )

    expected_result = pd.DataFrame(
        [
            ["A", ("sub1", "sub5")],
            ["A", ("sub1", "sub3")],
            ["A", ("sub3", "sub5")],
        ],
        columns=[AVAIL_COL, SUBJ_COL],
        index=[0, 0, 0],
    )

    result = _base._get_matches_from_slots(
        slots, availabilities_column=AVAIL_COL, availability_subject_column=SUBJ_COL
    )
    assert isinstance(result, pd.DataFrame)
    assert result.equals(expected_result)


def test__apply_exclusions():
    SUBJ_COL = "subj"
    EXCL_SUBJ_COLS = ["s1", "s2"]

    matches = pd.DataFrame(
        [
            ["A", ("sub1", "sub5")],
            ["A", ("sub1", "sub3")],
            ["A", ("sub3", "sub5")],
        ],
        columns=["avail", SUBJ_COL],
        index=[0, 0, 0],
    )
    exclusions = pd.DataFrame(
        [
            ["e1", "sub1", "sub3"],
        ],
        columns=["excl", EXCL_SUBJ_COLS[0], EXCL_SUBJ_COLS[1]],
    )
    expected_result = matches.loc[[True, False, True]]

    result = _base._apply_exclusions(
        matches,
        exclusions,
        availability_subject_column=SUBJ_COL,
        exclusions_subject_columns=EXCL_SUBJ_COLS,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.equals(expected_result)


def test_base_backend():
    AVAIL_COL = "avail"
    SUBJ_COL = "subj"
    EXCL_SUBJ_COLS = ["s1", "s2"]

    class TestBackend(_base.BackendBase):
        def __init__(self) -> None:
            self.subject_features = ["a", "b", "c"]
            self.availability_subject_column = SUBJ_COL
            self.availabilities_column = AVAIL_COL
            self.exclusions_subject_columns = EXCL_SUBJ_COLS

        def get_subjects(self) -> None:
            return

        def get_availabilities(self) -> pd.DataFrame:
            return pd.DataFrame(
                [
                    ["sub1", "A"],
                    ["sub2", "B"],
                    ["sub5", "A"],
                    ["sub3", "A"],
                    ["sub4", "C"],
                ],
                columns=[SUBJ_COL, AVAIL_COL],
            )

        def get_exclusions(self) -> pd.DataFrame:
            return pd.DataFrame(
                [
                    ["e1", "sub1", "sub3"],
                ],
                columns=["excl", EXCL_SUBJ_COLS[0], EXCL_SUBJ_COLS[1]],
            )

    expected_result = pd.DataFrame(
        [
            ["A", ("sub1", "sub5")],
            ["A", ("sub3", "sub5")],
        ],
        columns=["avail", SUBJ_COL],
        index=[0, 0],
    )

    be = TestBackend()
    result = be.get_all_matches(exclusions=True)
    assert isinstance(result, pd.DataFrame)
    assert result.equals(expected_result)
