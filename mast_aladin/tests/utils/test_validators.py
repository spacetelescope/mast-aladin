import mast_aladin.utils.validators as validators

from astropy.table import QTable
import pytest


class TestUtils:
    def test_is_valid_s3_uri(self):
        uri = "s3://my-bucket/my-file.parquet"
        result = validators.is_valid_s3_uri(uri)
        assert result is True

    def test_non_s3_uri(self):
        uri = "http://my-bucket/my-file.parquet"
        result = validators.is_valid_s3_uri(uri)
        assert result is False

    def test_file_is_not_s3_uri(self):
        uri = "file:///path/to/my-file.parquet"
        result = validators.is_valid_s3_uri(uri)
        assert result is False


@pytest.mark.parametrize("ra, dec", [('ALPHA_J2000', 'DELTA_J2000'), ('RA', 'DEC'),
                                     ('RA_deg', 'DEC_deg'), ('matchra', 'matchdec'),
                                     ('ra', 'dec'), ('ra_img', 'dec_img'),
                                     ('radeg', 'decdeg'), ('ramean', 'decmean'),
                                     ('s_ra', 's_dec'), ('sci_ra', 'sci_dec'),
                                     ('targ_ra', 'targ_dec'), ('trgposra', 'trgposdec')],
                         ids=lambda x: f"ra={x[0]}, dec={x[1]}")
def test_guess_ra_dec_columns(ra, dec):
    tab = QTable({ra: [10.0], dec: [-5.0]})

    guess_ra, guess_dec = validators.guess_coord_cols(tab)
    assert guess_ra == ra
    assert guess_dec == dec


@pytest.mark.parametrize("ra, dec", [("radial_velocity", "decade"),
                                     ("integrated", "decrement"),
                                     ("parallax", "deconvolve")])
def test_guess_coord_column_exclude(ra, dec):
    tab = QTable({ra: [10.0], dec: [-5.0]})

    guess_ra, guess_dec = validators.guess_coord_cols(tab)
    assert guess_ra == '---'
    assert guess_dec == '---'


@pytest.mark.parametrize("ra_meta, dec_meta",
                         [("pos.eq.ra", "pos.eq.dec"),
                          ("pos.eq.ra;meta.main", "pos.eq.dec;meta.main")])
def test_guess_ucd_column(ra_meta, dec_meta):
    tab = QTable({'pos1': [10.0], 'pos2': [-5.0]})
    tab['pos1'].meta['ucd'] = ra_meta
    tab['pos2'].meta['ucd'] = dec_meta

    guess_ra, guess_dec = validators.guess_coord_cols(tab)
    assert guess_ra == 'pos1'
    assert guess_dec == 'pos2'
