import fsspec
from astropy.table import Table


def table_from_s3(s3_uri, include_column_names=None):
    """
    Load a parquet file from S3 and return it as an astropy Table.

    parameters
    ----------
    s3_uri : str
        The URI to the parquet file in S3.
    include_column_names: list[str]
        List of column names from the remote parquet table to stream into an astropy Table.

    returns
    -------
    astropy.table.Table
        The loaded table.
    """
    fsspec_filesystem = fsspec.filesystem(protocol='s3', anon=True)
    file_stream = fsspec_filesystem.open(s3_uri)

    return Table.read(file_stream, include_names=include_column_names)
