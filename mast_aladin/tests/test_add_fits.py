import pytest
import re
import warnings

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS


def create_wcs():
    w = WCS(naxis=2)
    w.wcs.crpix = [5, 5]
    w.wcs.cdelt = [-0.000277, 0.000277]
    w.wcs.crval = [0, 0]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    return w


def create_example_fits():
    data = np.ones((10, 10))

    w = create_wcs()
    wcs_header = w.to_header(relax=True)

    hdu_list = fits.HDUList([
        fits.PrimaryHDU(header=wcs_header),
        fits.ImageHDU(data=data, header=wcs_header)
    ])
    return hdu_list


def create_example_fits_with_sip():
    data = np.ones((10, 10))

    w = create_wcs()
    w.wcs.ctype = ["RA---TAN-SIP", "DEC--TAN-SIP"]

    # fake SIP terms
    from astropy.wcs import Sip
    A = np.zeros((3, 3))
    B = np.zeros((3, 3))
    Ap = np.zeros((3, 3))
    Bp = np.zeros((3, 3))
    w.sip = Sip(A, B, Ap, Bp, w.wcs.crpix)

    wcs_header = w.to_header(relax=True)

    hdu_list = fits.HDUList([
        fits.PrimaryHDU(),
        fits.ImageHDU(data=data, header=wcs_header)
    ])

    return hdu_list


def create_empty_fits():

    hdu_list = fits.HDUList([
        fits.PrimaryHDU(),
    ])
    return hdu_list


@pytest.fixture
def fits_no_sip():
    return create_example_fits()


@pytest.fixture
def fits_with_sip():
    return create_example_fits_with_sip()


@pytest.fixture
def fits_empty():
    return create_empty_fits()


def test_add_fits(MastAladin_app, fits_no_sip):
    """Test add_fits raises no warnings for valid fits."""

    with warnings.catch_warnings(record=True) as w:
        MastAladin_app.add_fits(fits_no_sip)
        assert len(w) == 0


def test_fits_with_sip(MastAladin_app, fits_with_sip):
    """Test add_fits raises no warning for valid fits with sip."""

    with warnings.catch_warnings(record=True) as w:
        MastAladin_app.add_fits(fits_with_sip)
        assert len(w) == 0


def test_empty_fits(MastAladin_app, fits_empty):
    """Test add_fits raises ValueError for empty fits."""

    with pytest.raises(
        ValueError,
        match=re.escape("No data in extension 0")
    ):
        MastAladin_app.add_fits(fits_empty)


def test_image_options(MastAladin_app, fits_no_sip):
    """Test add_fits with image options raises no warnings for valid fits."""

    with warnings.catch_warnings(record=True) as w:
        MastAladin_app.add_fits(fits_no_sip, name="test", colormap="viridis")
        assert len(w) == 0
