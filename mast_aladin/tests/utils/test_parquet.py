import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import io
from astropy.table import Table

import mast_aladin.utils.parquet as parquet

TEST_PARQUET_PATH = Path(__file__).parent / '../data/r0034201001001001001_0001_wfi01_f087_cat.parquet'  # noqa: E501
TEST_S3_URI = 's3://some-bucket/r0034201001001001001_0001_wfi01_f087_cat.parquet'


def _load_test_parquet_bytes():
    """Load parquet file bytes once at module level."""
    with open(TEST_PARQUET_PATH, 'rb') as f:
        return f.read()


TEST_PARQUET_BYTES = _load_test_parquet_bytes()


@pytest.fixture
def mock_s3_filesystem():
    """Fixture that provides a mock S3 filesystem with test parquet data."""
    with patch('mast_aladin.utils.parquet.fsspec.filesystem') as mock_filesystem:
        mock_fs = Mock()
        mock_filesystem.return_value = mock_fs
        file_like_object = io.BytesIO(TEST_PARQUET_BYTES)
        mock_fs.open.return_value = file_like_object
        yield mock_filesystem, mock_fs


class TestTableFromParquetS3:
    def test_table_from_parquet_s3(self, mock_s3_filesystem):
        """Test loading a parquet file from S3 using a mocked s3 filesystem."""
        mock_filesystem, mock_fs = mock_s3_filesystem
        s3_uri = TEST_S3_URI

        result = parquet.table_from_s3(s3_uri)

        assert isinstance(result, Table)
        assert len(result) > 0

        mock_filesystem.assert_called_once_with(protocol='s3', anon=True)
        mock_fs.open.assert_called_once_with(s3_uri)

    def test_table_from_parquet_s3_with_kwargs(self, mock_s3_filesystem):
        """Test that kwargs are passed to astropy.Table.read."""
        mock_filesystem, mock_fs = mock_s3_filesystem
        s3_uri = TEST_S3_URI

        result = parquet.table_from_s3(s3_uri, include_column_names=["ra", "dec"])

        assert isinstance(result, Table)
        assert result.colnames == ['ra', 'dec']
        mock_fs.open.assert_called_once_with(s3_uri)
