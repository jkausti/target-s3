"""s3 target sink class, which handles writing streams."""

from __future__ import annotations

import datetime
import time

import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow.fs import S3FileSystem
from singer_sdk.exceptions import ConfigValidationError
from singer_sdk.sinks import BatchSink

NOW = datetime.datetime.utcnow()


class s3Sink(BatchSink):
    """s3 target sink class."""

    def __init__(self, target, schema, stream_name, key_properties) -> None:
        super().__init__(
            target=target,
            schema=schema,
            stream_name=stream_name,
            key_properties=key_properties,
        )

        self._pq_writer: pq.ParquetWriter = None
        self._pa_schema: pa.Schema = None

    max_size = 10000

    def get_s3_path(self) -> str:
        """Function to process S3 path into correct format."""

        path = self.config.get("path")
        folder_structure = self.config.get("folder_structure")

        if path.startswith("s3://"):
            path = path[5:]
        else:
            pass

        if path.endswith("/"):
            path = path[:-1]
        else:
            pass

        if folder_structure == "simple":
            s3_path = f"{path}/{self.stream_name}/{self.stream_name}.parquet"
        elif folder_structure == "date_hierarchy":
            s3_path = f"{path}/{self.stream_name}/{NOW.year}/{NOW.month}/{NOW.day}/{self.stream_name}__{NOW.isoformat()}.parquet"
        else:
            raise ConfigValidationError(
                'Invalid value for configuration key "folder_structure". Only values "simple" and "date_hierarchy" are supported.'
            )

        return s3_path

    @property
    def pq_writer(self) -> pq.ParquetWriter:
        """Initiates and returns the pyarrow ParquetWriter"""

        s3 = S3FileSystem(
            access_key=self.config.get("AWS_ACCESS_KEY_ID"),
            secret_key=self.config.get("AWS_SECRET_ACCESS_KEY"),
            region=self.config.get("aws_region"),
        )

        if not self._pq_writer:

            if not self.pa_schema:
                raise ValueError("No schema set for writing.")

            self._pq_writer = pq.ParquetWriter(
                where=self.get_s3_path(),
                filesystem=s3,
                schema=self.pa_schema,
            )

        return self._pq_writer

    @property
    def pa_schema(self):
        return self._pa_schema

    @pa_schema.setter
    def pa_schema(self, value):
        """Setter for _pa_schema"""
        self._pa_schema = value

    def process_batch(self, context: dict) -> None:
        """Process the batch."""

        table = pa.Table.from_pylist(context["records"])
        self.pa_schema = table.schema

        writer = self.pq_writer
        writer.write_table(table)

    def clean_up(self) -> None:

        writer = self.pq_writer
        writer.close()
        return super().clean_up()
