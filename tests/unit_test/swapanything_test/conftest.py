import json
from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest
from typing_extensions import TypedDict

__here__ = Path(__file__).parent
__data__ = __here__.parent / "data"


@pytest.fixture
def SUBJECTS_TABLE_NAME() -> str:
    return "subjects"


@pytest.fixture
def AVAILABILITIES_TABLE_NAME() -> str:
    return "availabilities"


@pytest.fixture
def SUBJECT_FEATURES() -> list[str]:
    subject_features = [
        "Growth Stage",
        "Goals",
        "Ruolo",
        "Customers",
        "Interessi",
        "Lingue Parlate",
    ]
    return subject_features


@pytest.fixture
def AVAILABILITY_SUBJECT_COLUMN() -> str:
    return "subj"


@pytest.fixture
def AVAILABILITIES_COLUMN() -> str:
    return "avail"


@pytest.fixture
def SUBJECTS_RECORDS() -> list[dict]:
    return json.loads((__data__ / "subjects_records.json").read_bytes())


@pytest.fixture
def AVAILABILITIES_RECORDS() -> list[dict]:
    return json.loads((__data__ / "availabilities_records.json").read_bytes())


def _cleanup_record(
    r: TypedDict("AirtableRecord", {"id": str, "createdTime": str, "fields": dict}),
    cols: list[str],
):
    r = deepcopy(r)
    r["fields"] = {k: v for k, v in r["fields"].items() if k in cols}
    return r


@pytest.fixture
def CLEAN_SUBJECTS_RECORDS(
    SUBJECTS_RECORDS: list[dict], SUBJECT_FEATURES: list[str]
) -> list[dict]:
    rec = [_cleanup_record(r, ["recID"] + SUBJECT_FEATURES) for r in SUBJECTS_RECORDS]
    return rec


@pytest.fixture
def CLEAN_AVAILABILITIES_RECORDS(
    AVAILABILITIES_RECORDS: list[dict],
    AVAILABILITIES_COLUMN: str,
    AVAILABILITY_SUBJECT_COLUMN: str,
) -> list[dict]:
    rec = [
        _cleanup_record(
            r, ["recID", AVAILABILITIES_COLUMN, AVAILABILITY_SUBJECT_COLUMN]
        )
        for r in AVAILABILITIES_RECORDS
    ]
    return rec


@pytest.fixture
def SUBJECTS_DF(CLEAN_SUBJECTS_RECORDS: list[dict]) -> pd.DataFrame:
    records = (
        pd.DataFrame(r["fields"] for r in CLEAN_SUBJECTS_RECORDS)
        .rename(columns={"recID": "subject_id"})
        .set_index("subject_id")
    )
    return records


@pytest.fixture
def AVAILABILITIES_DF(
    CLEAN_AVAILABILITIES_RECORDS: list[dict],
    AVAILABILITY_SUBJECT_COLUMN: str,
    AVAILABILITIES_COLUMN: str,
) -> pd.DataFrame:
    records = (
        pd.DataFrame(r["fields"] for r in CLEAN_AVAILABILITIES_RECORDS)
        .rename(
            columns={
                "recID": "availability_id",
                AVAILABILITY_SUBJECT_COLUMN: "subject_id",
                AVAILABILITIES_COLUMN: "availabilities",
            }
        )
        .set_index("availability_id")
    )
    return records
