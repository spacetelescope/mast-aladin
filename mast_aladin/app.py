import io
import os

from ipyaladin import Aladin
from mast_table import MastTable

from astropy.coordinates import SkyCoord
from astropy.io import fits
from regions import (
    Region,
    Regions,
    PolygonSkyRegion
)
from pathlib import Path
from astropy.wcs import WCS

from mast_aladin.aida import AID
from mast_aladin.mixins import DelayUntilRendered
from mast_aladin.overlay.overlay_manager import OverlayManager
from mast_aladin.overlay.mast_overlay import MastOverlay
from ipyaladin.elements.error_shape import (
    CircleError,
    EllipseError,
    _error_radius_conversion_factor,
)

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

        self._overlays_dict = OverlayManager(self)
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
        asdf : Union[str, rdd]
            The ASDF image to load in the widget. It can be given as a path (either a
            string or as a `roman_datamodels.datamodels._datamodels.ImageModel`).
        image_options : any
            The options for the image. See the `Aladin Lite image options
            <https://cds-astro.github.io/aladin-lite/global.html#ImageOptions>`_

        """

        if isinstance(asdf, str):
            if not os.path.exists(asdf):
                raise ValueError(
                    f"The file path given {asdf} does not exist, so no ASDF file "
                    "can be loaded."
                )

            try:
                asdf_file = rdd.open(asdf)
            except Exception as e:
                raise ValueError(
                    f"Invalid Roman Datamodel ASDF structure in {asdf}. "
                    "Ensure the file is accessible and a valid Roman Datamodel."
                ) from e

        elif isinstance(asdf, rdd._datamodels.ImageModel):
            asdf_file = asdf
        else:
            raise TypeError(
                "The provided ASDF was not given as a string or roman_datamodel, "
                "so no ASDF file could be loaded."
            )

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
        self, f, extension = 1, **image_options
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

    def add_markers(
        self, markers, **catalog_options
    ):
        # Wraps add_markers in ipyaladin to add overlay handling.
        # See ipyaladin for definitions of parameters.

        if not isinstance(markers, list):
            markers = [markers]

        catalog_options = self._overlays_dict.common_overlay_handling(
            catalog_options, "catalog_python"
        )

        overlay_info = self._overlays_dict.add_overlay(
            {
                "type": "marker",
                "markers": [marker.__dict__ for marker in markers],
                "update_info": markers,
                "options": catalog_options,
            }
        )

        super().add_markers(markers, **catalog_options)

        return overlay_info

    def add_catalog_from_URL(
        self, votable_URL, votable_options
    ):
        # Wraps add_catalog_from_URL in ipyaladin to add overlay handling.
        # See ipyaladin for definitions of parameters.
        if votable_options is None:
            votable_options = {}

        votable_options = self._overlays_dict.common_overlay_handling(
            votable_options, "catalog_python"
        )

        overlay_info = self._overlays_dict.add_overlay(
            {
                "type": "catalog",
                "votable_URL": votable_URL,
                "options": votable_options,
            }
        )

        super().add_catalog_from_URL(votable_URL, votable_options)

        return overlay_info

    def add_table(
        self,
        table,
        *,
        shape="cross",
        **table_options,
    ):
        # Wraps add_table in ipyaladin to add overlay handling.
        # See ipyaladin for definitions of parameters.
        if isinstance(shape, CircleError):
            table_options["circle_error"] = {
                "radius": shape.radius,
                "conversion_radius": _error_radius_conversion_factor(
                    table[shape.radius].unit, shape.probability_threshold
                ),
            }
            table_options["shape"] = shape.default_shape
        elif isinstance(shape, EllipseError):
            table_options["ellipse_error"] = {
                "maj_axis": shape.maj_axis,
                "min_axis": shape.min_axis,
                "angle": shape.angle,
                "conversion_angle": _error_radius_conversion_factor(
                    table[shape.angle].unit
                ),
                "conversion_maj_axis": _error_radius_conversion_factor(
                    table[shape.maj_axis].unit, shape.probability_threshold
                ),
                "conversion_min_axis": _error_radius_conversion_factor(
                    table[shape.min_axis].unit, shape.probability_threshold
                ),
            }
            table_options["shape"] = shape.default_shape
        else:
            table_options["shape"] = shape
        table_bytes = io.BytesIO()
        table.write(table_bytes, format="votable")

        table_options = self._overlays_dict.common_overlay_handling(
            table_options, "catalog_python"
        )

        overlay_info = self._overlays_dict.add_overlay(
            {
                "type": "table",
                "table": table,
                "options": table_options,
            }
        )
        shape = table_options.pop("shape", None)

        super().add_table(table, shape=shape, **table_options)

        return overlay_info

    def add_graphic_overlay_from_region(
        self,
        region,
        **graphic_options,
    ):
        """Add an overlay graphic layer to the Aladin Lite widget.

        Parameters
        ----------
        region: `~regions.CircleSkyRegion`, `~regions.EllipseSkyRegion`,
                `~regions.LineSkyRegion`,`~regions.PolygonSkyRegion`,
                `~regions.RectangleSkyRegion`, `~regions.Regions`, or a list of these.
            The region(s) to add in Aladin Lite. It can be given as a supported region
            or a list of regions from the
            `regions package <https://astropy-regions.readthedocs.io>`_.
        graphic_options: keyword arguments
            The options for the graphic overlay. Use Region visual for region options.
            See `Aladin Lite's graphic overlay options
            <https://cds-astro.github.io/aladin-lite/A.html>`_

        See Also
        --------
        add_graphic_overlay_from_stcs: for shapes described as STC-S strings.

        Notes
        -----
        The possible `~regions.RegionVisual` options correspond to the
        Aladin Lite / ipyaladin parameters:

        .. table:: Correspondence between options
            :widths: auto

            ============== ===================== ======================
            RegionVisual        AladinLite              ipyaladin
            ============== ===================== ======================
            edgecolor      color                 color
            facecolor      fillColor             fill_color
            color          color and fillColor   color and fill_color
            alpha          opacity               opacity
            linewidth      lineWidth             line_width
            ============== ===================== ======================

        """
        # Remove this docstring in favor of inheritance after this PR is merged:
        # https://github.com/cds-astro/ipyaladin/pull/175

        # Wraps add_graphic_overlay_from_region in ipyaladin to add overlay handling.
        # See ipyaladin for definitions of parameters.

        # Check if the region is a list of regions or a single
        # Region and convert it to a list of Regions
        if isinstance(region, Regions):
            region_list = region.regions
        elif not isinstance(region, list):
            region_list = [region]
        else:
            region_list = region

        regions_infos = []
        for region_element in region_list:
            if not isinstance(region_element, Region):
                raise ValueError(
                    "region must a `regions` object or a list of `regions` objects. "
                    "See the documentation for the supported region types."
                )

            from ipyaladin.utils._region_converter import RegionInfos

            # Define behavior for each region type
            regions_infos.append(RegionInfos(region_element).to_clean_dict())

        graphic_options = self._overlays_dict.common_overlay_handling(
            graphic_options, "overlay_python"
        )

        overlay_info = self._overlays_dict.add_overlay(
            {
                "type": "overlay_region",
                "regions_infos": regions_infos,
                "update_info": region_list,
                "options": graphic_options,
            }
        )

        super().add_graphic_overlay_from_region(region, **graphic_options)

        return overlay_info

    def add_graphic_overlay_from_stcs(
        self, stc_string, **overlay_options
    ):
        # Wraps add_graphic_overlay_from_stcs in ipyaladin to add overlay handling.
        # See ipyaladin for definitions of parameters.

        overlay_options = self._overlays_dict.common_overlay_handling(
            overlay_options, "overlay_python"
        )

        region_list = [stc_string] if isinstance(stc_string, str) else stc_string
        regions_infos = [
            {
                "region_type": "stcs",
                "infos": {"stcs": region_element},
                "options": overlay_options,
            }
            for region_element in region_list
        ]

        overlay_info = self._overlays_dict.add_overlay(
            {
                "type": "overlay_stcs",
                "regions_infos": regions_infos,
                "update_info": region_list,
                "options": overlay_options,
            }
        )

        super().add_graphic_overlay_from_stcs(stc_string, **overlay_options)

        return overlay_info

    def remove_overlay(self, overlay):
        """Remove an overlay.

        Parameters
        ----------
        overlay : str(s) or `~mast_aladin.MastOverlay`
            The overlay name (str) or MastOverlay object to be removed.

        Raises
        ------
        TypeError
            Overlays are not provided as `~mast_aladin.MastOverlay` or names.
        ValueError
            Overlay does not exist.
        """

        if isinstance(overlay, MastOverlay):
            overlay_names = [overlay.name]
        elif isinstance(overlay, str):
            overlay_names = [overlay]
        elif isinstance(overlay, (list, tuple)):
            overlay_names = [
                o.name if isinstance(o, MastOverlay) else o for o in overlay
            ]
        else:
            raise TypeError(
                "overlay must be a str, MastOverlay, or iterable of these."
            )

        super().remove_overlay(overlay_names)

        for name in overlay_names:
            if name not in self._overlays_dict:
                raise ValueError(
                    f"Cannot remove overlayer `{name}` since this layer does not exist."
                )

            self._overlays_dict.pop(name)

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
