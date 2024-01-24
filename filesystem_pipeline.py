import os
import dlt

try:
    from .filesystem import FileItemDict, filesystem, readers, read_parquet  # type: ignore
except ImportError:
    from filesystem import (
        FileItemDict,
        filesystem,
        readers,
        read_parquet,
    )


def swamp_hose() -> None:
    print("In Swamp Hose")
    pipeline = dlt.pipeline(
        pipeline_name="swamp_hose",
        destination='duckdb',
        dataset_name="loading_dock",
    )
    # When using the readers resource, you can specify a filter to select only the files you
    # want to load including a glob pattern. If you use a recursive glob pattern, the filenames
    # will include the path to the file inside the bucket_url.
    # PARQUET reading
    parquet_reader = readers(file_glob="sessions.parquet").read_parquet()
    # load both folders together to specified tables
    load_info = pipeline.run(
        [
            parquet_reader.with_name("src_ga_sessions"),
        ]
    )
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    swamp_hose()
