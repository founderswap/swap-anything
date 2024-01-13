import pandas as pd
import pytest
from swapanything_backend import _base


def test_incomplete_base_backend():
    AVAIL_COL = "avail"
    SUBJ_COL = "subj"
    EXCL_SUBJ_COLS = ["s1", "s2"]

    class TestBackend(_base.BackendBase):
        def __init__(self) -> None:
            self.subject_features = ["a", "b", "c"]
            self.availability_subject_column = SUBJ_COL
            self.availabilities_column = AVAIL_COL
            self.exclusions_subject_columns = EXCL_SUBJ_COLS

    with pytest.raises(TypeError, match=r"Can't instantiate abstract class"):
        TestBackend()


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
            return

        def get_exclusions(self) -> pd.DataFrame:
            return

    TestBackend()
