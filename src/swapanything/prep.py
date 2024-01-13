from itertools import combinations
from typing import Annotated, Iterable, Optional, Tuple, Union

import pandas as pd


class BackendError(Exception):
    pass


def get_matching_subjects_by_slot(
    availabilities: pd.DataFrame,
    slot_col: str,
    subject_col: str,
) -> pd.DataFrame:
    matching_subjects_by_slot = (
        availabilities.groupby(slot_col)
        .agg({subject_col: lambda x: tuple(x)})
        .reset_index(col_level=1)
    )
    matching_subjects_by_slot = matching_subjects_by_slot[
        matching_subjects_by_slot[subject_col].apply(len) > 1
    ]
    return matching_subjects_by_slot


def get_matches_from_slots(
    matching_subjects_by_slot: pd.DataFrame,
    slot_col: str,
    subject_col: str,
) -> pd.DataFrame:
    matches = (
        matching_subjects_by_slot.set_index(slot_col)[subject_col]
        .apply(lambda a: list(combinations(a, 2)))
        .reset_index()
        .explode(subject_col)
    )
    matches[subject_col] = matches[subject_col].apply(sorted).apply(tuple)
    return matches


def apply_exclusions(
    matches: pd.DataFrame,
    exclusions: pd.DataFrame,
    subject_col: str,
    exclusions_subject_columns: Annotated[Iterable[str], 2],
) -> pd.DataFrame:
    exclude_matchings = exclusions[exclusions_subject_columns]
    exclude_matchings = [tuple(sorted(x)) for x in exclude_matchings.values]
    exluded_mask = matches[subject_col].isin(exclude_matchings)
    matches = matches.loc[~exluded_mask]
    return matches


def get_all_matches(
    availabilities: pd.DataFrame,
    subject_col: str,
    slot_col: str,
    subjects_new_col_name: Optional[str] = None,
    slots_new_col_name: Optional[str] = None,
    exclusions: Union[pd.DataFrame, None] = None,
    exclusions_subject_columns: Tuple[str, str] = None,
    return_matching_subjects_by_slot: bool = False,
    availabilities_by_slot: bool = False,
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
    if not availabilities_by_slot:
        matching_subjects_by_slot = get_matching_subjects_by_slot(
            availabilities,
            slot_col=slot_col,
            subject_col=subject_col,
        )
    else:
        matching_subjects_by_slot = availabilities

    matches = get_matches_from_slots(
        matching_subjects_by_slot,
        slot_col=slot_col,
        subject_col=subject_col,
    )

    if isinstance(exclusions, pd.DataFrame):
        matches = apply_exclusions(
            matches,
            exclusions=exclusions,
            subject_col=subject_col,
            exclusions_subject_columns=exclusions_subject_columns,
        )

    # go from:
    #  [{"avail": "A", "subj": (1, 2)},
    #   {"avail": "B", "subj": (1, 2)}]
    # to:
    #  [{"subj": (1, 2), "avail": ("A", "B")}]
    matches = matches.sort_values(
        # Sort to guarantee idempotency downstream
        [slot_col]
    )
    matches = matches.groupby(subject_col)[[slot_col]].agg(tuple).reset_index()

    if slots_new_col_name:
        matches = matches.rename(columns={slot_col: slots_new_col_name})

    if subjects_new_col_name:
        matches = matches.rename(columns={subject_col: subjects_new_col_name})

    if return_matching_subjects_by_slot:
        return matches, matching_subjects_by_slot
    else:
        return matches
