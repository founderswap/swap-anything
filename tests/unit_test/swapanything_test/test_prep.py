import pandas as pd
from swapanything import prep


def test__get_matching_subjects_by_slot():
    SLOT_COL = "avail"
    SUBJ_COL = "subj"
    df = pd.DataFrame(
        [
            ["sub1", "A"],
            ["sub2", "B"],
            ["sub5", "A"],
            ["sub3", "A"],
            ["sub4", "C"],
        ],
        columns=[SUBJ_COL, SLOT_COL],
    )

    expected_result = pd.DataFrame(
        [
            ["A", ("sub1", "sub5", "sub3")],
        ],
        columns=[SLOT_COL, SUBJ_COL],
    )

    result = prep.get_matching_subjects_by_slot(
        availabilities=df,
        subject_col=SUBJ_COL,
        slot_col=SLOT_COL,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.equals(expected_result)


def test__get_matches_from_slots():
    SLOT_COL = "avail"
    SUBJ_COL = "subj"
    slots = pd.DataFrame(
        [
            ["A", ("sub1", "sub5", "sub3")],
        ],
        columns=[SLOT_COL, SUBJ_COL],
    )

    expected_result = pd.DataFrame(
        [
            ["A", ("sub1", "sub5")],
            ["A", ("sub1", "sub3")],
            ["A", ("sub3", "sub5")],
        ],
        columns=[SLOT_COL, SUBJ_COL],
        index=[0, 0, 0],
    )

    result = prep.get_matches_from_slots(slots, slot_col=SLOT_COL, subject_col=SUBJ_COL)
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

    result = prep.apply_exclusions(
        matches,
        exclusions,
        subject_col=SUBJ_COL,
        exclusions_subject_columns=EXCL_SUBJ_COLS,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.equals(expected_result)


def test_get_all_matches():
    SLOT_COL = "avail"
    SUBJ_COL = "subj"
    EXCL_SUBJ_COLS = ["s1", "s2"]
    availabilities = pd.DataFrame(
        [
            ["sub3", "A"],
            ["sub1", "A"],
            ["sub2", "B"],
            ["sub5", "A"],
            ["sub4", "C"],
        ],
        columns=[SUBJ_COL, SLOT_COL],
    )

    exclusions = pd.DataFrame(
        [
            ["e1", "sub1", "sub3"],
        ],
        columns=["excl", EXCL_SUBJ_COLS[0], EXCL_SUBJ_COLS[1]],
    )

    expected_result = pd.DataFrame(
        [
            [("sub1", "sub5"), ("A",)],
            [("sub3", "sub5"), ("A",)],
        ],
        columns=[SUBJ_COL, "avail"],
    )

    result = prep.get_all_matches(
        availabilities=availabilities,
        subject_col=SUBJ_COL,
        slot_col=SLOT_COL,
        exclusions=exclusions,
        exclusions_subject_columns=EXCL_SUBJ_COLS,
    )
    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {SUBJ_COL, SLOT_COL}
    assert result.equals(expected_result)

    availabilities_by_slot = prep.get_matching_subjects_by_slot(
        availabilities=availabilities,
        subject_col=SUBJ_COL,
        slot_col=SLOT_COL,
    )
    result2 = prep.get_all_matches(
        availabilities=availabilities_by_slot,
        subject_col=SUBJ_COL,
        slot_col=SLOT_COL,
        exclusions=exclusions,
        exclusions_subject_columns=EXCL_SUBJ_COLS,
        availabilities_by_slot=True,
    )
    assert result2.equals(result)

    result3, matching_subjects_by_slot = prep.get_all_matches(
        availabilities=availabilities,
        subject_col=SUBJ_COL,
        slot_col=SLOT_COL,
        exclusions=exclusions,
        exclusions_subject_columns=EXCL_SUBJ_COLS,
        return_matching_subjects_by_slot=True,
        slots_new_col_name="slots_new_col_name",
        subjects_new_col_name="subjects_new_col_name",
    )
    assert isinstance(result3, pd.DataFrame)
    assert result3.to_dict(orient="records") == [
        {"subjects_new_col_name": ("sub1", "sub5"), "slots_new_col_name": ("A",)},
        {"subjects_new_col_name": ("sub3", "sub5"), "slots_new_col_name": ("A",)},
    ]
    assert matching_subjects_by_slot.to_dict(orient="records") == [
        {"avail": "A", "subj": ("sub3", "sub1", "sub5")}
    ]
