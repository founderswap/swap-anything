from abc import ABC, abstractmethod
from itertools import combinations
from typing import Annotated, Iterable

import pandas as pd


def _get_matching_subjects_by_slot(
    availabilities: pd.DataFrame,
    availabilities_column: str,
    availability_subject_column: str,
) -> pd.DataFrame:
    matching_subjects_by_slot = (
        availabilities.groupby(availabilities_column)
        .agg({availability_subject_column: lambda x: tuple(x)})
        .reset_index(col_level=1)
    )
    matching_subjects_by_slot = matching_subjects_by_slot[
        matching_subjects_by_slot[availability_subject_column].apply(len) > 1
    ]
    return matching_subjects_by_slot


def _get_matches_from_slots(
    matching_subjects_by_slot: pd.DataFrame,
    availabilities_column: str,
    availability_subject_column: str,
) -> pd.DataFrame:
    matches = (
        matching_subjects_by_slot.set_index(availabilities_column)[
            availability_subject_column
        ]
        .apply(lambda a: list(combinations(a, 2)))
        .reset_index()
        .explode(availability_subject_column)
    )
    matches[availability_subject_column] = matches[availability_subject_column].apply(
        lambda x: tuple(sorted(x))
    )
    return matches


def _apply_exclusions(
    matches: pd.DataFrame,
    exclusions: pd.DataFrame,
    availability_subject_column: str,
    exclusions_subject_columns: Annotated[Iterable[str], 2],
) -> pd.DataFrame:
    exclude_matchings = exclusions[exclusions_subject_columns]
    exclude_matchings = [tuple(sorted(x)) for x in exclude_matchings.values]
    exluded_mask = matches[availability_subject_column].isin(exclude_matchings)
    matches = matches.loc[~exluded_mask]
    return matches


class BackendBase(ABC):
    subject_features: list[str]
    availability_subject_column: str
    availabilities_column: str
    exclusions_subject_columns: Annotated[Iterable[str], 2]

    @abstractmethod
    def get_subjects(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def get_availabilities(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def get_exclusions(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError()

    def get_all_matches(
        self,
        availabilities: pd.DataFrame | None = None,
        exclusions: pd.DataFrame | None | bool = None,
        return_matching_subjects_by_slot: bool = False,
    ) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
        # initialize things
        if not availabilities:
            availabilities = self.get_availabilities()
        if isinstance(exclusions, bool) and exclusions:
            exclusions = self.get_exclusions()

        matching_subjects_by_slot = _get_matching_subjects_by_slot(
            availabilities,
            availabilities_column=self.availabilities_column,
            availability_subject_column=self.availability_subject_column,
        )
        matches = _get_matches_from_slots(
            matching_subjects_by_slot,
            availabilities_column=self.availabilities_column,
            availability_subject_column=self.availability_subject_column,
        )

        if isinstance(exclusions, pd.DataFrame):
            matches = _apply_exclusions(
                matches,
                exclusions=exclusions,
                availability_subject_column=self.availability_subject_column,
                exclusions_subject_columns=self.exclusions_subject_columns,
            )

        if return_matching_subjects_by_slot:
            return matches, matching_subjects_by_slot
        else:
            return matches
