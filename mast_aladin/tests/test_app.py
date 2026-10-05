from mast_aladin.app import MastAladin, gca
from mast_aladin.utils.validators import guess_coord_cols
from unittest.mock import Mock, patch
from astropy.table import Table, QTable
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


def test_guess_ra_dec_columns(MastAladin_app):
    """
    Test that the guess_coord_cols function correctly identifies RA and Dec columns
    from a given astropy table.
    """
    # these are the unique variations in VO TAP query outputs
    ra_variations = ['ALPHA_J2000', 'RA', 'RA_deg', 'matchra', 'ra', 'ra_img', 'radeg',
                     'ramean', 's_ra', 'sci_ra', 'targ_ra', 'trgposra']
    dec_variations = ['DEC', 'DEC_deg', 'DELTA_J2000', 'dec', 'decdeg', 'decl',
                      'decl_img', 'decmean', 'matchdec', 's_dec', 'sci_dec', 'targ_dec',
                      'trgposdec']

    variations_to_pass = list(zip(ra_variations, dec_variations))

    for v in variations_to_pass:
        ra, dec = v
        tab = QTable({ra: [10.0], dec: [-5.0]})

        guess_ra = guess_coord_cols('ra', tab)
        guess_dec = guess_coord_cols('dec', tab)
        assert guess_ra == ra
        assert guess_dec == dec
        MastAladin_app.add_table(tab)

    # check that certain strings that contain 'ra' and 'dec' substrings are not
    # misidentified as coordinate columns
    tab = QTable({'radial_velocity': [10.0], 'fluxradius': [5.0], 'decrement': [1.0]})
    guess_ra = guess_coord_cols('ra', tab)
    guess_dec = guess_coord_cols('dec', tab)
    # none of the column names in the input table should have been identified as RA or Dec columns,
    # so they should be set as a placeholder value of '---'
    assert guess_ra == '---'
    assert guess_dec == '---'
