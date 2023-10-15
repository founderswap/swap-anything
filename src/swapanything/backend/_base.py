from abc import ABC, abstractmethod

import pandas as pd


class BackendBase(ABC):
    @abstractmethod
    def get_subjects(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def get_availabilities(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError()
