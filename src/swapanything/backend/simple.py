from typing import Annotated, Iterable, Optional

import pandas as pd

from ._base import BackendBase


class SimpleBackend(BackendBase):
    subject_features: list[str]
    availability_subject_column: str
    availabilities_column: str
    exclusions_subject_columns: Annotated[Iterable[str], 2]

    def __init__(
        self,
        availabilities: pd.DataFrame,
        availability_subject_column: str,
        availabilities_column: str,
        subject_features: Optional[list[str]] = None,
        subjects: Optional[pd.DataFrame] = None,
        exclusions: Optional[pd.DataFrame] = None,
        exclusions_subject_columns: Annotated[Iterable[str], 2] = [],
    ) -> None:
        self.availabilities = availabilities
        self.availability_subject_column = availability_subject_column
        self.availabilities_column = availabilities_column
        self.exclusions = exclusions
        self.exclusions_subject_columns = exclusions_subject_columns

        if not isinstance(subjects, pd.DataFrame):
            self.subjects = availabilities[
                [availability_subject_column]
            ].drop_duplicates()
            self.subject_features = subject_features or []  # force empty
        else:
            self.subjects = subjects
            self.subject_features = subject_features

    def get_subjects(self, *args, **kwargs) -> pd.DataFrame:
        return self.subjects

    def get_availabilities(self, *args, **kwargs) -> pd.DataFrame:
        return self.availabilities

    def get_exclusions(self, *args, **kwargs) -> pd.DataFrame:
        return self.exclusions
