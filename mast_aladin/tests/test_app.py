from mast_aladin.app import MastAladin, gca
from unittest.mock import Mock, patch
from astropy.table import Table
import pytest


def test_current_app(MastAladin_app):
    # MastAladin_app should be the current instance of the app
    assert gca() == MastAladin_app

    # create new app instance
    instance2 = MastAladin()

    # gca should refer to the newly instantiated app:
    assert gca() == instance2


@patch("mast_aladin.utils.parquet.table_from_s3")
def test_add_astropy_table(mock_table_from_s3, MastAladin_app):
    """
    Test that the add_table method functions as defined by ipyaladin when
    given an astropy table, and that parquet logic is not invoked.
    """
    table = Table()

    result = MastAladin_app.add_table(table)

    mock_table_from_s3.assert_not_called()
    assert result["type"] == "table"


@patch("mast_aladin.utils.parquet.table_from_s3")
def test_add_parquet_table(mock_table_from_s3, MastAladin_app):
    """
    Test that the add_table method correctly handles parquet URIs and invokes
    the super method from ipyaladin.
    """
    mock_table = Table()
    mock_table_from_s3.return_value = mock_table
    parquet_uri = "s3://some-bucket/test.parquet"

    result = MastAladin_app.add_table(
        parquet_uri,
        shape="circle",
        include_column_names=["ra", "dec"]
    )

    mock_table_from_s3.assert_called_once_with(
        parquet_uri,
        ["ra", "dec"]
    )
    assert result["type"] == "table"
    assert result['options']['shape'] == "circle"


@patch("mast_aladin.utils.parquet.table_from_s3")
def test_add_invalid_table(mock_table_from_s3, MastAladin_app):
    """
    Test that an invalid parquet table not from S3 raises a ValueError
    """
    mock_table = Mock()
    mock_table_from_s3.return_value = mock_table
    parquet_uri = "https://some-bucket/test.parquet"

    with pytest.raises(ValueError):
        MastAladin_app.add_table(parquet_uri)

    mock_table_from_s3.assert_not_called()


def test_show_invalid_locs():
    """
    Test that the show method correctly raises errors for invalid locs.
    """
    ma = MastAladin()

    # check invalid loc type
    with pytest.raises(TypeError, match="Invalid loc type provided. Must be a string."):
        ma.show(loc=1234)

    # check invalid sidecar anchor
    with pytest.raises(ValueError, match="Invalid anchor provided. Must be one of"):
        ma.show(loc="sidecar:invalid")

    # check invalid popout anchor
    with pytest.raises(
        ValueError,
        match="Invalid anchor provided. Must be 'window' or 'tab'"
    ):
        ma.show(loc="popout:invalid")

    # check invalid loc str
    with pytest.raises(
        ValueError,
        match="Invalid loc provided. Must be 'inline', 'sidecar', or 'popout'."
    ):
        ma.show(loc="invalid")
