from ipyaladin import Aladin
from mast_table import MastTable

from astropy.coordinates import SkyCoord
from astropy.io import fits

from regions import (
    PolygonSkyRegion
)
from pathlib import Path
from astropy.wcs import WCS

from IPython.display import display
from sidecar import Sidecar
import ipywidgets as widgets
from ipypopout import PopoutButton

from mast_aladin.aida import AIDA
from mast_aladin.mixins import DelayUntilRendered
import mast_aladin.utils.parquet as parquet
from mast_aladin.utils.validators import is_valid_s3_uri

import roman_datamodels.datamodels as rdd
import os


__all__ = [
    'MastAladin',
    'gca',
]

# store reference to the latest instantiation:
_latest_instantiated_app = None


class MastAladin(Aladin, DelayUntilRendered, AIDA):
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

        global _latest_instantiated_app
        _latest_instantiated_app = self

        self.sidecar = kwargs.get("sidecar", None)
        self.popout_button = PopoutButton(self, window_features="popup,width=800,height=600")

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

    def add_table(
        self, table, include_names=None, shape="cross", **table_options
    ):
        """Wrapper on the ipyaladin.widget.Aladin.add_table method that enables loading of
        alternate table types. See ipyaladin.widget.Aladin.add_table for more details on the
        underlying implementation.

        Parameters
        ----------
        table : `~astropy.table.table.QTable` or `~astropy.table.table.Table` or `str`
            The table to add. Valid types are astropy table and S3 URIs of parquet files.
        include_names : list[str]
            List of column names from the remote parquet table to stream into mast-aladin.
        shape : str | `~ipyaladin.CircleError` | `~ipyaladin.EllipseError`
            The shape to draw for each source. It accepts the strings "square",
            "circle", "plus", "cross", "rhomb", and "triangle" as well as the two
            specific classes `ipyaladin.CircleError` and `ipyaladin.EllipseError`
            that adapt the size of the drawn shapes (circles or ellipses) to error
            columns.
            See ipyaladin example notebook `04_Importing_Tables`.
        **table_options : dict
            Keyword arguments. The possible values are documented in `Aladin Lite's table options
            <https://cds-astro.github.io/aladin-lite/global.html#CatalogOptions>`
        """
        if isinstance(table, (os.PathLike, str)):
            if is_valid_s3_uri(table) and str(table).endswith('.parquet'):
                table = parquet.table_from_s3(table, include_names)
            else:
                raise ValueError(
                    f"table='{table}' is not a valid S3 URI for a parquet table."
                )

        return super().add_table(table, shape=shape, **table_options)

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

    def show(self, loc="sidecar:split-right", title="mast-aladin", ref=None):
        """
        Display MastAladin.

        Parameters
        ----------
        loc : str, optional (default "sidecar:split-right")
            Location to display the MastAladin. Supported locations:
                "inline": Displays the MastAladin inline in a notebook.
                "sidecar": Displays the MastAladin in a separate JupyterLab window from the
                    notebook, with location decided by 'anchor'. Anchor options available from
                    ``jupyterlab-sidecar`` are:
                        {'split-right', 'split-left', 'split-top', 'split-bottom', 'tab-before',
                         'tab-after', 'right'}
                    Example loc for a sidecar at the bottom is ``loc='sidecar:split-bottom'``.
                "popout": Display the MastAladin in a detached display. By default, a new
                    window will open (browser popup permissions required). Anchor options are:
                        * ``popout:window`` (default, opens MastAladin in a new, detached popout)
                        * ``popout:tab`` (opens MastAladin in a new, detached tab in your browser)

        title : str, optional (default "mast-aladin")
            The title of the sidecar tab, only applicable to a "sidecar" display.

        ref: Sidecar, optional (default None)
            An existing reference sidecar. Opens the new sidecar display with its anchor defined
            relative to the ref sidecar. Only applicable to a "sidecar" display.

        """
        valid_anchors = [
            "split-right", "split-left", "split-top", "split-bottom",
            "tab-before", "tab-after", "right", None
        ]

        if type(loc) is not str:
            raise ValueError("Invalid loc provided. Must be a string.")

        if loc == "inline":
            display(self)
        elif loc.startswith("sidecar"):
            anchor = None if loc == "sidecar" else loc.split(":")[-1]

            if anchor not in valid_anchors:
                raise ValueError(
                    "Invalid anchor provided. Must be one of the available from "
                    "``jupyterlab-sidecar``. Valid anchors are: "
                    f"{valid_anchors[:-1]}")

            sc = Sidecar(title=title, anchor=anchor, ref=ref)
            with sc:
                display(self)

        elif loc.startswith("popout"):
            anchor = None if loc == "popout" else loc.split(":")[-1]

            if not hasattr(self, "_popout_output"):
                self._popout_output = widgets.Output()

            with self._popout_output:
                self.height = 600
                display(self.popout_button)

            if anchor in (None, "window"):
                self.popout_button.open_window()
            elif anchor == "tab":
                self.popout_button.open_tab()
            else:
                raise ValueError(
                    "Invalid anchor provided. Must be 'window' or 'tab'."
                )


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
