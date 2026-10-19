from mast_aladin.app import MastAladin, gca
from unittest.mock import Mock, patch
from astropy.table import Table
from astroquery.exceptions import InvalidQueryError
from astroquery.mast import MastMissionsClass
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


ORIG_FILENAME = "r0034201001001001001_0001_wfi01_f087_coadd.asdf"
L3_FILESET_NAME = ORIG_FILENAME.rpartition('_')[0]


def _mock_mission_app():
    mission_app = Mock(spec=MastMissionsClass)
    l3_table = Table({"category": ["3"], "fileSetName": [L3_FILESET_NAME]})

    def get_unique_product_list(fileset_name):
        if fileset_name == L3_FILESET_NAME:
            return l3_table
        raise InvalidQueryError("no match")

    mission_app.get_unique_product_list.side_effect = get_unique_product_list
    return mission_app


@pytest.mark.parametrize("l4_filename", [
    "r0034201001001001001_0001_wfi01_f087_segm.asdf",
    "dummy.asdf",
])
def test_find_roman_level3_products_from_asdf(MastAladin_app, write_asdf_file, l4_filename):
    l4_path = write_asdf_file(l4_filename, orig_filename=ORIG_FILENAME)
    mission_app = _mock_mission_app()

    result = MastAladin_app.find_roman_level3_products(str(l4_path), mission_app)

    assert len(result) > 0
    assert result["fileSetName"][0] == L3_FILESET_NAME


@pytest.mark.parametrize("l4_filename", [
    "r0034201001001001001_0001_wfi01_f087_cat.parquet",
    "dummy.parquet",
])
def test_find_roman_level3_products_from_parquet(MastAladin_app, write_parquet_file, l4_filename):
    l4_path = write_parquet_file(l4_filename, orig_filename=ORIG_FILENAME)
    mission_app = _mock_mission_app()

    result = MastAladin_app.find_roman_level3_products(str(l4_path), mission_app)

    assert len(result) > 0
    assert result["fileSetName"][0] == L3_FILESET_NAME
