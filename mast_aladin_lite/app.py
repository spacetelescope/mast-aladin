from ipyaladin import Aladin
from mast_aladin_lite.aida import AID
from mast_aladin_lite.table import MastTable
from mast_aladin_lite.mixins import DelayUntilRendered
from mast_aladin_lite.overlay.overlay_manager import OverlayManager
from mast_aladin_lite.overlay.mast_overlay import MastOverlay
import io
from ipyaladin.elements.error_shape import (
    CircleError,
    EllipseError,
    _error_radius_conversion_factor,
)

try:
    from regions import (
        Region,
        Regions,
    )
except ImportError:
    Region = None
    Regions = None

__all__ = [
    'MastAladin',
    'gca',
]

# store reference to the latest instantiation:
_latest_instantiated_app = None


class MastAladin(Aladin, DelayUntilRendered):

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

    def add_markers(
        self, markers, **catalog_options
    ):
        """Wraps add_markers in ipyaladin to add overlay handling.

        See ipyaladin for definitions of parameters.
        """
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
        """Wraps add_catalog_from_URL in ipyaladin to add overlay handling.

        See ipyaladin for definitions of parameters.
        """
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
        """Wraps add_table in ipyaladin to add overlay handling.

        See ipyaladin for definitions of parameters.
        """
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
        """Wraps add_graphic_overlay_from_region in ipyaladin to add overlay handling.

        See ipyaladin for definitions of parameters.
        """
        if Region is None:
            raise ModuleNotFoundError(
                "To read regions objects, you need to install the regions library with "
                "'pip install regions'."
            )

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
                    "region must a `~regions` object or a list of `~regions` objects. "
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
        """Wraps add_graphic_overlay_from_stcs in ipyaladin to add overlay handling.

        See ipyaladin for definitions of parameters.
        """

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
        """Wraps remove_overlay in ipyaladin to add overlay handling.

        Parameters
        ----------
        overlay : str(s) or MastOverlay(s)
            The overlay name (str) or MastOverlay object to be removed.

        Raises
        ------
        TypeError
            Overlays are not provided as MastOverlay or names.
        ValueError
            Overlay does not exist.

        See ipyaladin for definitions of its parameters.
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


def gca():
    """
    Get the current mast-aladin-lite application instance.
    If none exist, create a new one.

    Returns
    -------
    MastAladin
    """
    if _latest_instantiated_app is None:
        return MastAladin()

    return _latest_instantiated_app
