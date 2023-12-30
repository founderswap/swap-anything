from abc import ABC, abstractmethod
from typing import Annotated, Iterable, TypeVar

import pandas as pd


class BackendError(Exception):
    pass


class BackendBase(ABC):
    subject_features: list[str]
    availability_subject_column: str
    availabilities_column: str
    exclusions_subject_columns: Annotated[Iterable[str], 2]

    @abstractmethod
    def get_subjects(self, *args, **kwargs) -> pd.DataFrame:  # pragma: no cover
        raise NotImplementedError()

    @abstractmethod
    def get_availabilities(self, *args, **kwargs) -> pd.DataFrame:  # pragma: no cover
        raise NotImplementedError()

    @abstractmethod
    def get_exclusions(self, *args, **kwargs) -> pd.DataFrame:  # pragma: no cover
        raise NotImplementedError()


BackendType = TypeVar("BackendType", bound=BackendBase)
