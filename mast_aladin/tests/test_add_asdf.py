import os
import pytest
import re
import warnings

import numpy as np
import astropy.units as u
from astropy.modeling import models
from gwcs import coordinate_frames as cf, wcs as gwcs_wcs
from astropy.coordinates import ICRS


def create_example_gwcs(shape):
    """
    This is borrowed from imviz:
    https://github.com/spacetelescope/jdaviz/blob/main/jdaviz/configs/imviz/tests/utils.py
    """
    # Example adapted from photutils:
    #   https://github.com/astropy/photutils/blob/
    #   2825356f1d876cacefb3a03d104a4c563065375f/photutils/datasets/make.py#L821
    rho = np.pi / 3.0
    # Roman plate scale:
    scale = (0.11 * (u.arcsec / u.pixel)).to_value(u.deg / u.pixel)

    shift_by_crpix = (models.Shift((-shape[1] / 2) + 1)
                      & models.Shift((-shape[0] / 2) + 1))

    cd_matrix = np.array([[-scale * np.cos(rho), scale * np.sin(rho)],
                          [scale * np.sin(rho), scale * np.cos(rho)]])

    rotation = models.AffineTransformation2D(cd_matrix, translation=[0, 0])
    rotation.inverse = models.AffineTransformation2D(
        np.linalg.inv(cd_matrix), translation=[0, 0])

    tan = models.Pix2Sky_TAN()
    celestial_rotation = models.RotateNative2Celestial(197.8925, -1.36555556, 180.0)

    det2sky = shift_by_crpix | rotation | tan | celestial_rotation
    det2sky.name = 'linear_transform'

    detector_frame = cf.Frame2D(name='detector', axes_names=('x', 'y'), unit=(u.pix, u.pix))

    sky_frame = cf.CelestialFrame(reference_frame=ICRS(), name='icrs', unit=(u.deg, u.deg))

    pipeline = [(detector_frame, det2sky), (sky_frame, None)]

    wcs = gwcs_wcs.WCS(pipeline)
    wcs.bounding_box = [(0, shape[0]), (0, shape[1])]
    return wcs


def create_wfi_image_model(image_shape=(20, 10), **kwargs):
    """
    This is borrowed from imviz:
    https://github.com/spacetelescope/jdaviz/blob/main/jdaviz/configs/imviz/tests/utils.py

    Create a dummy Roman WFI ImageModel instance with valid values
    for attributes required by the schema.

    Requires roman_datamodels >= 0.14.2

    Parameters
    ----------
    image_shape : tuple
        Shape of the synthetic image to produce.

    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    data_model : `roman_datamodels.datamodel.ImageModel`

    """
    from roman_datamodels import datamodels as rdd

    model = rdd.ImageModel.create_fake_data(shape=image_shape, defaults=kwargs)

    # introduce synthetic gwcs:
    model.meta.wcs = create_example_gwcs(image_shape)
    return model


@pytest.fixture
def roman_imagemodel():
    return create_wfi_image_model()


def test_add_asdf(MastAladin_app, roman_imagemodel):
    """Test add_asdf raises no warnings for valid Roman ASDF."""

    with warnings.catch_warnings(record=True) as w:
        MastAladin_app.add_asdf(roman_imagemodel)
        assert len(w) == 0


def test_image_options(MastAladin_app, roman_imagemodel):
    """Test add_asdf with image options raises no warnings for valid Roman ASDF."""

    with warnings.catch_warnings(record=True) as w:
        MastAladin_app.add_asdf(roman_imagemodel, name="test", colormap="viridis")
        assert len(w) == 0


def test_invaid_filepath(MastAladin_app):
    """Test add_asdf raises error for invalid filepaths."""

    invalid_filepath = os.path.join(
        os.path.dirname(__file__), "data", "this_is_fake.asdf"
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            f"The file path given {invalid_filepath} does not exist, so no ASDF file "
            "can be loaded."
        )
    ):
        MastAladin_app.add_asdf(invalid_filepath)


def test_invaid_asdf(MastAladin_app):
    """Test add_asdf raises error for invalid ASDF file."""

    # this is the example.asdf file demo-ed here:
    # https://www.asdf-format.org/projects/asdf/en/latest/asdf/overview.html
    invalid_asdf_filepath = os.path.join(
        os.path.dirname(__file__), "data", "invalid_example.asdf"
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            f"Invalid ASDF structure: missing required key 'roman' "
            f"in {invalid_asdf_filepath}. Ensure the file is a valid Roman Datamodel."
        )
    ):
        MastAladin_app.add_asdf(invalid_asdf_filepath)
