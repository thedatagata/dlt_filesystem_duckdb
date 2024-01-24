"""Reads files in s3, gs or azure buckets using fsspec and provides convenience resources for chunked reading of various file formats"""
from typing import Iterator, List, Optional, Tuple, Union

import dlt
from dlt.common.typing import copy_sig
from dlt.sources import DltResource
from dlt.sources.filesystem import FileItem, FileItemDict, fsspec_filesystem, glob_files
from dlt.sources.credentials import FileSystemCredentials

from .helpers import (
    AbstractFileSystem,
    FilesystemConfigurationResource,
    fsspec_from_resource,
)
from .readers import ReadersSource, _read_parquet
from .settings import DEFAULT_CHUNK_SIZE


@dlt.source(_impl_cls=ReadersSource, spec=FilesystemConfigurationResource)
def readers(
    bucket_url: str = dlt.config.value,
    credentials: Union[FileSystemCredentials, AbstractFileSystem] = dlt.secrets.value,
    file_glob: Optional[str] = "*",
) -> Tuple[DltResource, ...]:
    return (
        filesystem(bucket_url, credentials, file_glob=file_glob)
        | dlt.transformer(name="read_parquet")(_read_parquet),
    )


@dlt.resource(
    primary_key="file_url", spec=FilesystemConfigurationResource, standalone=True
)
def filesystem(
    bucket_url: str = dlt.config.value,
    credentials: Union[FileSystemCredentials, AbstractFileSystem] = dlt.secrets.value,
    file_glob: Optional[str] = "*",
    files_per_page: int = DEFAULT_CHUNK_SIZE,
    extract_content: bool = False,
) -> Iterator[List[FileItem]]:

    fs_client, bucket_url = fsspec_filesystem(bucket_url)

    files_chunk: List[FileItem] = []
    for file_model in glob_files(fs_client, bucket_url, file_glob):
        file_dict = FileItemDict(file_model, credentials)
        if extract_content:
            file_dict["file_content"] = file_dict.read_bytes()
        files_chunk.append(file_dict)  

        # wait for the chunk to be full
        if len(files_chunk) >= files_per_page:
            yield files_chunk
            files_chunk = []
    if files_chunk:
        yield files_chunk

read_parquet = dlt.transformer(standalone=True)(_read_parquet)
