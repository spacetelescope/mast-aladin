from astropy.io import fits
import pytest
import numpy as np


class BaseImviz:
    @pytest.fixture(autouse=True)
    def setup_class(self, imviz_helper):
        arr = np.ones((10, 10))

        hdu1 = fits.ImageHDU(arr, name='SCI')
        hdu1.header.update({
            'CTYPE1': 'RA---TAN',
            'CUNIT1': 'deg',
            'CDELT1': -0.00404486401600876,
            'CRPIX1': 6.0,
            'CRVAL1': 9.423506267012352,
            'NAXIS1': 0,
            'CTYPE2': 'DEC--TAN',
            'CUNIT2': 'deg',
            'CDELT2': 0.004044864016008764,
            'CRPIX2': 6.0,
            'CRVAL2': -33.71313687167955,
            'NAXIS2': 0
        })
        imviz_helper.load(hdu1, format="Image", data_label='has_wcs_1')

        self.imviz = imviz_helper
        glue_viewer = imviz_helper.app.get_viewers_of_cls('ImvizImageView')[0]
        self.viewer = glue_viewer
        self.viewer.shape = (100, 100)
        self.viewer.state._set_axes_aspect_ratio(1)
