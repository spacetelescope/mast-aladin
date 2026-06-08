from ipyaladin import Aladin
from mast_table import MastTable

from astropy.coordinates import SkyCoord
from astropy.io import fits
from regions import (
    PolygonSkyRegion
)
from pathlib import Path
from astropy.wcs import WCS

from mast_aladin.aida import AID
from mast_aladin.mixins import DelayUntilRendered

import roman_datamodels.datamodels as rdd

__all__ = [
    'MastAladin',
    'gca',
]

# store reference to the latest instantiation:
_latest_instantiated_app = None


class MastAladin(Aladin, DelayUntilRendered):
    """
    An Aladin-lite widget with enhanced support for
    datasets from `MAST <https://mast.stsci.edu/>`_, built on
    top of `ipyaladin.widget.Aladin`.
    """
    def __init__(self, *args, **kwargs):
        # set ICRSd as the default visible coordinate system
        # in aladin-lite:
        kwargs.setdefault('coo_frame', 'ICRSd')

        super().__init__(*args, **kwargs)

        # the `aid` attribute gives access to methods from the
        # Astro Image Display (AID) API
        self.aid = AID(self)

        global _latest_instantiated_app
        _latest_instantiated_app = self

        self.sidecar = kwargs.get("sidecar", None)

    def load_table(
        self,
        table,
        load_footprints=True,
        update_viewport=True,
        unique_column=None
    ):
        table_widget = MastTable(
            table,
            app=self,
            unique_column=unique_column,
            update_viewport=update_viewport
        )

        if load_footprints:
            if 's_region' in table.colnames:
                self.add_graphic_overlay_from_stcs(table['s_region'])
            else:
                raise ValueError(
                    "The table does not contain an `s_region` column, so no "
                    "footprints can be loaded."
                )

        return table_widget

    def add_asdf(
        self, asdf, **image_options
    ):
        """Load an ASDF image into the widget.

        Parameters
        ----------
        asdf : Union[str or Path-like, rdd]
            The ASDF image to load in the widget. It can be given as a path (either a
            string or as a `roman_datamodels.datamodels._datamodels.ImageModel`).
        image_options : any
            The options for the image. See the `Aladin Lite image options
            <https://cds-astro.github.io/aladin-lite/global.html#ImageOptions>`_

        """
        if isinstance(asdf, rdd._datamodels.ImageModel):
            asdf_file = asdf
        else:
            asdf_file = rdd.open(asdf)

        wcs_header = fits.Header(asdf_file.meta.wcs.to_fits()[0])

        hdu_list = fits.HDUList(
            [
                fits.PrimaryHDU(header=wcs_header),
                fits.ImageHDU(
                    header=wcs_header,
                    data=asdf_file.data
                )
            ]
        )

        self.add_fits(hdu_list, **image_options)

    def add_fits(
        self, f, extension=1, **image_options
    ):
        """Load a FITS image into the widget.

        Parameters
        ----------
        f : Union[str, Path, HDUList]
            The FITS image to load in the widget. It can be given as a path (either a
            string or a `pathlib.Path` object), or as an `astropy.io.fits.HDUList`.
        extension: int, optional
            FITS extension containing the image data to load. Default is 1.
        image_options : any
            The options for the image. See the `Aladin Lite image options
            <https://cds-astro.github.io/aladin-lite/global.html#ImageOptions>`_

        """

        # Wraps add_fits in ipyaladin to temporarily handle SIP.
        # See ipyaladin for definitions of parameters.

        is_path = isinstance(f, (Path, str))
        if is_path:
            fits_file = fits.open(f)
        else:
            fits_file = f

        if len(fits_file) == 1:
            extension = 0

        data = fits_file[extension].data
        wcs = WCS(fits_file[extension].header)

        if data is None:
            raise ValueError(
                f"No data in extension {extension}."
            )

        wcs.sip = None

        wcs_header = wcs.to_header()

        hdu_list = fits.HDUList(
            [
                fits.PrimaryHDU(header=wcs_header),
                fits.ImageHDU(
                    header=wcs_header,
                    data=data
                )
            ]
        )

        super().add_fits(hdu_list, **image_options)

    def get_viewport_region(self, center=False):
        """Return a `regions.PolygonSkyRegion` representing the perimeter of the
        MastAladin viewport.

        Parameters
        ----------
        center : bool, optional
            If `False` (default), return a region where the vertices are the
            the outer corners of the corner pixels; otherwise the vertices will
            be the corner pixel centers.

        Returns
        -------
        `regions.PolygonSkyRegion`
            Region with vertices representing the corners of the current field
            of view in the viewport.
        """

        sky_corners = SkyCoord(
            self.wcs.calc_footprint(undistort=False, center=center),
            unit='deg'
        )
        return PolygonSkyRegion(sky_corners)


def gca():
    """
    Get the current mast-aladin application instance.
    If none exist, create a new one.

    Returns
    -------
    `~mast_aladin.app.MastAladin`
    """
    if _latest_instantiated_app is None:
        return MastAladin()

    return _latest_instantiated_app
