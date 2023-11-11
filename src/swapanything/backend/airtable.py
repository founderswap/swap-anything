from collections.abc import Iterator
from typing import Annotated, Iterable

import pandas as pd
import pyairtable as airtable
from pydantic import BaseModel, Field, PastDatetime, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# from swapanything import models as m
from ._base import BackendBase


class AirtableRecord(BaseModel):
    record_id: str = Field(alias="id")
    created_timestamp: PastDatetime = Field(alias="createdTime")
    record_fields: dict = Field(alias="fields")


class AirtableResponse(BaseModel):
    records: list[AirtableRecord]

    def iter_records(self) -> Iterator[dict]:
        for record in self.records:
            yield record.record_fields

    def to_pandas(self) -> pd.DataFrame:
        df = pd.DataFrame(self.iter_records())
        return df


class AirTableBackend(BaseSettings, BackendBase):
    # Manually adding again to help pylance and other
    # linters not to get crazy
    subject_features: list[str]
    availability_subject_column: str
    availabilities_column: str
    exclusions_subject_columns: Annotated[Iterable[str], 2]

    subjects_table_name: str
    availabilities_table_name: str
    exclusions_table_name: str
    client_id: SecretStr = Field(..., validation_alias="AIRTABLE_BASE_ID")
    client_secret: SecretStr = Field(..., validation_alias="AIRTABLE_API_KEY")

    model_config = SettingsConfigDict(case_sensitive=False, env_prefix="SWPAT_")

    def _get_table(
        self,
        table_name: str,
        **options,
    ) -> list[dict]:
        table = airtable.Table(  # type: ignore
            api_key=self.client_secret.get_secret_value(),
            base_id=self.client_id.get_secret_value(),
            table_name=table_name,
        )

        all = table.all(**options)
        return all

    def get_subjects(self, formula: str | None = None) -> pd.DataFrame:
        table = self._get_table(
            table_name=self.subjects_table_name,
            fields=["recID", *self.subject_features],
            formula=formula,
        )
        table = AirtableResponse.model_validate({"records": table})
        table = (
            table.to_pandas()
            .rename(columns={"recID": "subject_id"})
            .set_index("subject_id")
        )
        return table

    def get_exclusions(self, formula: str | None = None) -> pd.DataFrame:
        table = self._get_table(
            table_name=self.exclusions_table_name,
            fields=["recID", *self.exclusions_subject_columns],
            formula=formula,
        )
        table = AirtableResponse.model_validate({"records": table})
        table = (
            table.to_pandas()
            .rename(columns={"recID": "exclusion_id"})
            .set_index("exclusion_id")
        )
        return table

    def get_availabilities(self, formula: str | None = None) -> pd.DataFrame:
        table = self._get_table(
            table_name=self.availabilities_table_name,
            fields=[
                "recID",
                self.availability_subject_column,
                self.availabilities_column,
            ],
            formula=formula,
        )
        table = AirtableResponse.model_validate({"records": table})
        table = (
            table.to_pandas()
            .rename(
                columns={
                    "recID": "availability_id",
                    self.availability_subject_column: "subject_id",
                    self.availabilities_column: "availabilities",
                }
            )
            .set_index("availability_id")
        )
        return table
