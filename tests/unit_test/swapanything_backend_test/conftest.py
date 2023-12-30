import json
from copy import deepcopy
from pathlib import Path
from typing import Annotated

import pandas as pd
import pytest
from typing_extensions import TypedDict

__here__ = Path(__file__).parent
__data__ = __here__.parent / "data"


class AirtableRecord(TypedDict):
    id: str
    createdTime: str
    fields: dict


@pytest.fixture
def SUBJECTS_TABLE_NAME() -> str:
    return "subjects"


@pytest.fixture
def AVAILABILITIES_TABLE_NAME() -> str:
    return "availabilities"


@pytest.fixture
def EXCLUSIONS_TABLE_NAME() -> str:
    return "exclusions"


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
def EXCLUSOIONS_SUBJECT_COLUMNS() -> Annotated[list[str], 2]:
    return ["subj1", "subj2"]


@pytest.fixture
def SUBJECTS_RECORDS() -> list[AirtableRecord]:
    return json.loads((__data__ / "subjects_records.json").read_bytes())


@pytest.fixture
def AVAILABILITIES_RECORDS() -> list[AirtableRecord]:
    return json.loads((__data__ / "availabilities_records.json").read_bytes())


@pytest.fixture
def EXCLUSIONS_RECORDS() -> list[AirtableRecord]:
    return json.loads((__data__ / "exclusions_records.json").read_bytes())


def _cleanup_record(
    r: AirtableRecord,
    cols: list[str],
) -> AirtableRecord:
    r = deepcopy(r)
    r["fields"] = {k: v for k, v in r["fields"].items() if k in cols}
    return r


@pytest.fixture
def CLEAN_SUBJECTS_RECORDS(
    SUBJECTS_RECORDS: list[AirtableRecord], SUBJECT_FEATURES: list[str]
) -> list[AirtableRecord]:
    rec = [_cleanup_record(r, ["recID"] + SUBJECT_FEATURES) for r in SUBJECTS_RECORDS]
    return rec


@pytest.fixture
def CLEAN_EXCLUSIONS_RECORDS(
    EXCLUSIONS_RECORDS: list[AirtableRecord], EXCLUSOIONS_SUBJECT_COLUMNS: list[str]
) -> list[AirtableRecord]:
    rec = [
        _cleanup_record(r, ["recID"] + EXCLUSOIONS_SUBJECT_COLUMNS)
        for r in EXCLUSIONS_RECORDS
    ]
    return rec


@pytest.fixture
def CLEAN_AVAILABILITIES_RECORDS(
    AVAILABILITIES_RECORDS: list[AirtableRecord],
    AVAILABILITIES_COLUMN: str,
    AVAILABILITY_SUBJECT_COLUMN: str,
) -> list[AirtableRecord]:
    rec = [
        _cleanup_record(
            r, ["recID", AVAILABILITIES_COLUMN, AVAILABILITY_SUBJECT_COLUMN]
        )
        for r in AVAILABILITIES_RECORDS
    ]
    return rec


@pytest.fixture
def SUBJECTS_DF(CLEAN_SUBJECTS_RECORDS: list[AirtableRecord]) -> pd.DataFrame:
    records = (
        pd.DataFrame(r["fields"] for r in CLEAN_SUBJECTS_RECORDS)
        .rename(columns={"recID": "subject_id"})
        .set_index("subject_id")
    )
    return records


@pytest.fixture
def AVAILABILITIES_DF(
    CLEAN_AVAILABILITIES_RECORDS: list[AirtableRecord],
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


@pytest.fixture
def EXCLUSIONS_DF(CLEAN_EXCLUSIONS_RECORDS: list[AirtableRecord]) -> pd.DataFrame:
    records = (
        pd.DataFrame(r["fields"] for r in CLEAN_EXCLUSIONS_RECORDS)
        .rename(columns={"recID": "exclusion_id"})
        .set_index("exclusion_id")
    )
    return records
