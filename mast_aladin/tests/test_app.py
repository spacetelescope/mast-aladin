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
    """
        Create a mocked `MastMissionsClass` instance that simulates the two-step
        `query_criteria` -> `get_unique_product_list` lookup used by
        `_extract_l3_from_metadata`.
        """
    mission_app = Mock(spec=MastMissionsClass)
    l3_table = Table({"category": ["3"], "fileSetName": [L3_FILESET_NAME], "productLevel": ["3"]})

    def query_criteria(**kwargs):
        # stand-in for the query object astroquery would normally build
        return kwargs

    def get_unique_product_list(query):
        if query.get("fileSetName") == L3_FILESET_NAME or "coordinates" in query:
            return l3_table
        raise InvalidQueryError("no match")

    mission_app.query_criteria.side_effect = query_criteria
    mission_app.get_unique_product_list.side_effect = get_unique_product_list
    return mission_app


def test_mock_mission_app_query_chain():
    """
    Unit test for the `_mock_mission_app` test helper: it should return the
    Level 3 product table for a matching fileSetName or coordinates-based
    query, and raise `InvalidQueryError` for any other query.
    """
    mission_app = _mock_mission_app()

    query = mission_app.query_criteria(fileSetName=L3_FILESET_NAME, productLevel=3)
    result = mission_app.get_unique_product_list(query)
    assert len(result) == 1
    assert result["fileSetName"][0] == L3_FILESET_NAME

    query = mission_app.query_criteria(coordinates="10d 20d", productLevel=3)
    result = mission_app.get_unique_product_list(query)
    assert len(result) == 1

    query = mission_app.query_criteria(fileSetName="nonexistent", productLevel=3)
    with pytest.raises(InvalidQueryError, match="no match"):
        mission_app.get_unique_product_list(query)


@pytest.fixture
def mock_rdd_open():
    """
    Patch the `mast_aladin.app.rdd.open` function to return a mock object
    with a `to_flat_dict` method that returns a dictionary containing
    the necessary metadata for `find_roman_level3_products` to recover
    the original Level 3 filename, since `find_roman_level3_products`
    uses `rdd.open` to read the file and extract metadata.
    """
    flat = {
           "roman.meta.filename": ORIG_FILENAME,
           "roman.meta.wcsinfo.ra": 10.0,
           "roman.meta.wcsinfo.dec": 20.0,
           "roman.meta.instrument.name": "WFI",
           "roman.meta.instrument.optical_element": "F087",
           "roman.meta.observation.execution_plan": "EP1",
           "roman.meta.observation.program": "P1",
           "roman.meta.coadd_info.exposure_time": 100.0}
    with patch("mast_aladin.app.rdd.open") as m:
        m.return_value.to_flat_dict.return_value = flat
        yield m


def test_find_roman_level3_products_from_asdf(MastAladin_app,
                                              write_asdf_file):
    """
    Test that `find_roman_level3_products` can extract the original Level 3 filename
    from a Level 4 ASDF file and return the corresponding Level 3 product table.
    It won't open the file, so rdd.open doesn't need to be called.
    """
    l4_path = write_asdf_file("r0034201001001001001_0001_wfi01_f087_segm.asdf",
                              orig_filename=ORIG_FILENAME)
    mission_app = _mock_mission_app()

    result = MastAladin_app.find_roman_level3_products(str(l4_path), mission_app)

    assert len(result) > 0
    assert result["fileSetName"][0] == L3_FILESET_NAME


def test_find_roman_level3_products_from_renamed_asdf(MastAladin_app,
                                                      write_asdf_file,
                                                      mock_rdd_open):
    """
    In practice, a renamed ASDF file will be opened by rdd.open, which will work for
    real Roman files because they are valid inputs for roman_datamodels.
    This test requires a mocked rdd.open to simulate the behavior of opening a renamed ASDF file
    since the pytest fixture `write_asdf_file` creates a minimal ASDF file that is not a
    valid Roman file and cannot be opened by rdd.open.
    """
    l4_path = write_asdf_file("dummy.asdf",
                              orig_filename=ORIG_FILENAME)
    mission_app = _mock_mission_app()

    result = MastAladin_app.find_roman_level3_products(str(l4_path), mission_app)

    mock_rdd_open.assert_called_once()
    assert len(result) > 0
    assert result["fileSetName"][0] == L3_FILESET_NAME


@pytest.mark.parametrize("l4_filename", [
    # standardized parquet filename for Roman Level 4 catalog product
    "r0034201001001001001_0001_wfi01_f087_cat.parquet",
    # file renamed by the user
    "dummy.parquet",
])
def test_find_roman_level3_products_from_parquet(MastAladin_app,
                                                 write_parquet_file,
                                                 l4_filename):
    """
    Test that `find_roman_level3_products` can find L3 products given any L4 parquet file.
    """
    l4_path = write_parquet_file(l4_filename, orig_filename=ORIG_FILENAME)
    mission_app = _mock_mission_app()

    result = MastAladin_app.find_roman_level3_products(str(l4_path), mission_app)

    assert len(result) > 0
    assert result["fileSetName"][0] == L3_FILESET_NAME


def test_find_roman_level3_products_invalid_file(MastAladin_app,
                                                 tmp_path):
    """
    A file that isn't ASDF or parquet, and whose name doesn't follow the L4
    naming convention, should raise a ValueError once all fallbacks fail.
    """
    l4_path = tmp_path / "some_random_file.fits"
    l4_path.touch()
    mission_app = _mock_mission_app()

    with pytest.raises(ValueError,
                       match="Could not extract original filename"):
        MastAladin_app.find_roman_level3_products(str(l4_path), mission_app)


def test_find_roman_level3_products_invalid_mission_app(MastAladin_app,
                                                        write_asdf_file):
    l4_path = write_asdf_file("dummy.asdf", orig_filename=ORIG_FILENAME)

    with pytest.raises(TypeError,
                       match="mission_app must be an instance of MastMissionsClass, not <class 'NoneType'>."):  # noqa: E501
        MastAladin_app.find_roman_level3_products(str(l4_path), None)
