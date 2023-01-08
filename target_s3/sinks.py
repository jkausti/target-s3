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

    max_size = 5

    def get_s3_path(self, path: str, folder_structure: str) -> str:
        """Function to process S3 path into correct format."""

        epoch = time.time()

        if path.startswith("s3://"):
            path = path[5:]
        else:
            pass

        if path.endswith("/"):
            path = path[:-1]
        else:
            pass

        if folder_structure == "simple":
            s3_path = f"{path}/{self.stream_name}/{self.stream_name}_{epoch}.parquet"
        elif folder_structure == "date_hierarchy":
            s3_path = f"{path}/{self.stream_name}/{NOW.year}/{NOW.month}/{NOW.day}/{self.stream_name}__{epoch}.parquet"
        else:
            raise ConfigValidationError(
                'Invalid value for configuration key "folder_structure". Only values "simple" and "date_hierarchy" are supported.'
            )

        return s3_path

    def process_batch(self, context: dict) -> None:
        """Process the batch."""

        table = pa.Table.from_pylist(context["records"])

        s3_path = self.get_s3_path(self.config.get("path"), self.config.get("folder_structure"))

        s3 = S3FileSystem(
            access_key=self.config.get("AWS_ACCESS_KEY_ID"),
            secret_key=self.config.get("AWS_SECRET_ACCESS_KEY"),
        )

        # write table
        pq.write_table(table=table, where=s3_path, filesystem=s3, compression="snappy")

        context["records"] = []
