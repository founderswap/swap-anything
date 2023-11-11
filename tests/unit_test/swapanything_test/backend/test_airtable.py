import re
from unittest.mock import MagicMock

import pandas as pd
import pytest
from swapanything.backend import airtable as be


@pytest.fixture
def BASE_ID() -> str:
    return "baseId"


@pytest.fixture
def API_KEY() -> str:
    return "apiKey"


@pytest.fixture
def mock_airtable_env_vars(
    monkeypatch: pytest.MonkeyPatch, BASE_ID: str, API_KEY: str
) -> None:
    monkeypatch.setenv("AIRTABLE_BASE_ID", BASE_ID)
    monkeypatch.setenv("AIRTABLE_API_KEY", API_KEY)


@pytest.fixture
def mock_airtable(
    monkeypatch: pytest.MonkeyPatch,
    CLEAN_SUBJECTS_RECORDS: list[dict],
    CLEAN_AVAILABILITIES_RECORDS: list[dict],
    CLEAN_EXCLUSIONS_RECORDS: list[dict],
    SUBJECTS_TABLE_NAME: str,
    AVAILABILITIES_TABLE_NAME: str,
    EXCLUSIONS_TABLE_NAME: str,
    mock_airtable_env_vars: None,
) -> MagicMock:
    """Make Airtable SDK return our mock subjects records."""
    # custom class to be the mock return value of requests.get()
    mock_airtable = MagicMock(be.airtable.Table)  # type: ignore
    mock_airtable.return_value = mock_airtable

    def get_records(*args, **kwargs) -> list[dict]:
        table_name = mock_airtable.call_args[1]["table_name"]
        if table_name == SUBJECTS_TABLE_NAME:
            return CLEAN_SUBJECTS_RECORDS
        elif table_name == AVAILABILITIES_TABLE_NAME:
            return CLEAN_AVAILABILITIES_RECORDS
        elif table_name == EXCLUSIONS_TABLE_NAME:
            return CLEAN_EXCLUSIONS_RECORDS
        else:
            raise NotImplementedError("No mock records for '%s'" % table_name)

    mock_airtable.all.side_effect = get_records

    monkeypatch.setattr("pyairtable.Table", mock_airtable)
    return mock_airtable


@pytest.fixture
def airtable_backend(
    SUBJECT_FEATURES: list[str],
    AVAILABILITY_SUBJECT_COLUMN: str,
    AVAILABILITIES_COLUMN: str,
    SUBJECTS_TABLE_NAME: str,
    AVAILABILITIES_TABLE_NAME: str,
    EXCLUSIONS_TABLE_NAME: str,
    EXCLUSOIONS_SUBJECT_COLUMNS: list[str],
    mock_airtable: None,
) -> be.AirTableBackend:
    backend = be.AirTableBackend(  # type: ignore
        subject_features=SUBJECT_FEATURES,
        availability_subject_column=AVAILABILITY_SUBJECT_COLUMN,
        availabilities_column=AVAILABILITIES_COLUMN,
        subjects_table_name=SUBJECTS_TABLE_NAME,
        availabilities_table_name=AVAILABILITIES_TABLE_NAME,
        exclusions_table_name=EXCLUSIONS_TABLE_NAME,
        exclusions_subject_columns=EXCLUSOIONS_SUBJECT_COLUMNS,
    )
    return backend


def test_backend_init(mock_airtable: MagicMock, BASE_ID: str, API_KEY: str):
    data = be.AirTableBackend(  # type: ignore
        subject_features=["a", "b"],
        availability_subject_column="availability_subject_column",
        availabilities_column="availabilities_column",
        subjects_table_name="subjects_table",
        availabilities_table_name="availabilities_table",
        exclusions_table_name="exclustions_table",
        exclusions_subject_columns=[
            "exclusions_subject_column1",
            "exclusions_subject_column2",
        ],
    )
    assert re.match(r"^\*{2,}$", str(data.client_id))  # all is more than 2 '*'
    assert re.match(r"^\*{2,}$", str(data.client_secret))
    assert data.client_id.get_secret_value() == BASE_ID
    assert data.client_secret.get_secret_value() == API_KEY


def test__get_table(
    mock_airtable: MagicMock,
    BASE_ID: str,
    API_KEY: str,
    SUBJECTS_TABLE_NAME: str,
    CLEAN_SUBJECTS_RECORDS: list[dict],
    SUBJECT_FEATURES: str,
) -> None:
    """Test the general method to retrieve a table using pyairtable SDK."""
    # Mock properties of initialized AirTableBackend
    airtable_backend_mock = MagicMock()
    airtable_backend_mock.client_secret.get_secret_value.return_value = API_KEY
    airtable_backend_mock.client_id.get_secret_value.return_value = BASE_ID

    # execute method only, using 'airtable_backend_mock' as 'self'
    table = be.AirTableBackend._get_table(
        airtable_backend_mock, SUBJECTS_TABLE_NAME, fields=SUBJECT_FEATURES
    )

    # Check that everything has been called properly
    mock_airtable.assert_called_once_with(
        api_key=API_KEY, base_id=BASE_ID, table_name=SUBJECTS_TABLE_NAME
    )
    mock_airtable.all.assert_called_once_with(fields=SUBJECT_FEATURES)

    # Check that results correspond
    assert table == CLEAN_SUBJECTS_RECORDS


def test_get_subjects(
    airtable_backend: be.AirTableBackend,
    mock_airtable: MagicMock,
    SUBJECTS_TABLE_NAME: str,
    SUBJECT_FEATURES: list[str],
    SUBJECTS_DF: pd.DataFrame,
    BASE_ID: str,
    API_KEY: str,
):
    df = airtable_backend.get_subjects(formula=None)
    mock_airtable.assert_called_once_with(
        api_key=API_KEY, base_id=BASE_ID, table_name=SUBJECTS_TABLE_NAME
    )
    mock_airtable.all.assert_called_once_with(
        fields=["recID"] + SUBJECT_FEATURES, formula=None
    )
    assert set(df.columns) == set(SUBJECT_FEATURES)
    assert df.equals(SUBJECTS_DF)


def test_get_availabilities(
    airtable_backend: be.AirTableBackend,
    mock_airtable: MagicMock,
    AVAILABILITIES_TABLE_NAME: str,
    AVAILABILITIES_DF: pd.DataFrame,
    AVAILABILITY_SUBJECT_COLUMN: str,
    AVAILABILITIES_COLUMN: str,
    BASE_ID: str,
    API_KEY: str,
):
    AVAIL_FEATURES = ["recID", AVAILABILITY_SUBJECT_COLUMN, AVAILABILITIES_COLUMN]
    df = airtable_backend.get_availabilities(formula=None)

    mock_airtable.assert_called_once_with(
        api_key=API_KEY, base_id=BASE_ID, table_name=AVAILABILITIES_TABLE_NAME
    )
    mock_airtable.all.assert_called_once_with(fields=AVAIL_FEATURES, formula=None)
    assert set(df.columns) == {"subject_id", "availabilities"}
    assert df.index.name == "availability_id"
    assert df.equals(AVAILABILITIES_DF)


def test_get_exclustions(
    airtable_backend: be.AirTableBackend,
    mock_airtable: MagicMock,
    EXCLUSIONS_TABLE_NAME: str,
    EXCLUSOIONS_SUBJECT_COLUMNS: list[str],
    EXCLUSIONS_DF: pd.DataFrame,
    BASE_ID: str,
    API_KEY: str,
):
    df = airtable_backend.get_exclusions(formula=None)
    mock_airtable.assert_called_once_with(
        api_key=API_KEY, base_id=BASE_ID, table_name=EXCLUSIONS_TABLE_NAME
    )
    mock_airtable.all.assert_called_once_with(
        fields=["recID"] + EXCLUSOIONS_SUBJECT_COLUMNS, formula=None
    )
    assert set(df.columns) == set(EXCLUSOIONS_SUBJECT_COLUMNS)
    assert df.equals(EXCLUSIONS_DF)
