from typing import TYPE_CHECKING, Any, Iterator

from dlt.common import json
from dlt.common.typing import copy_sig
from dlt.sources import TDataItems, DltResource, DltSource
from dlt.sources.filesystem import FileItemDict


def _read_parquet(
    items: Iterator[FileItemDict],
    chunksize: int = 10000,
) -> Iterator[TDataItems]:
    """Reads parquet file content and extract the data.

    Args:
        chunksize (int, optional): The number of files to process at once, defaults to 10.

    Returns:
        TDataItem: The file content
    """
    from pyarrow import parquet as pq

    for file_obj in items:
        with file_obj.open() as f:
            parquet_file = pq.ParquetFile(f)
            for rows in parquet_file.iter_batches(batch_size=chunksize):
                yield rows.to_pylist()


if TYPE_CHECKING:

    class ReadersSource(DltSource):
        """This is a typing stub that provides docstrings and signatures to the resources in `readers" source"""

        @copy_sig(_read_parquet)
        def read_parquet(self) -> DltResource:
            ...

else:
    ReadersSource = DltSource
