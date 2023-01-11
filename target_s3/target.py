"""s3 target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_s3.sinks import s3Sink


class Targets3(Target):
    """Sample target for s3."""

    name = "target-s3"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "AWS_ACCESS_KEY_ID",
            th.StringType,
            description="AWS Access Key ID used to authenticate programmatically to S3.",
            required=False,
        ),
        th.Property(
            "AWS_SECRET_ACCESS_KEY",
            th.StringType,
            description="AWS Secret Access Key used to authenticate programmatically to S3.",
            secret=True,
            required=False,
        ),
        th.Property(
            "path",
            th.StringType,
            description="The path to where the data should be stored. *REQUIRED*",
            required=True,
        ),
        th.Property(
            "folder_structure",
            th.StringType,
            default="simple",
            required=True,
            description="Determines the folder-structure. Alternatives are: 'simple', 'date_hierarchy' and 'both'.",
        ),
        th.Property(
            "filetype",
            th.StringType,
            default="parquet",
            required=True,
            description="Specifies the filetype to store the data as. Only parquet supported atm. *REQUIRED*",
        ),
    ).to_dict()

    default_sink_class = s3Sink


if __name__ == "__main__":
    Targets3.cli()
