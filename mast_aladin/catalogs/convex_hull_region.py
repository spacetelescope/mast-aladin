import numpy as np
from scipy.spatial import ConvexHull as ScipyConvexHullImpl
from .performance import PerformanceCatalog


def _polygon_vertices_to_stcs(vertices):
    """
    Convert an array of sky coordinates into a polygon STC-S region.

    Parameters
    ----------
    vertices : array with shape (N, 2)
        The vertices array has one column for RA and another for Dec in degrees
        in the ICRS coordinate frame for N vertices.

    Returns
    -------
    str
        STC-S region
    """
    return 'POLYGON ICRS ' + ' '.join(
        map(lambda x: " ".join(map("{0:f}".format, x)),
            vertices)
    )


class ConvexHullRegion(PerformanceCatalog):
    """
    Visualize a source catalog as scatter marks up to some number of points
    ``n_sources_max``. For ``>n_sources_max`` sources, swap out the scatter
    marks for a region representing a polygon that connects the outermost
    catalog coordinates (the convex hull).

    Uses scipy's `~scipy.spatial.ConvexHull`.
    """
    def __post_init__(self):
        """
        Compute the convex hull and save the result as an STC-S region.
        """
        ra_dec_stack = np.column_stack(
            (self.source_coords.ra.degree, self.source_coords.dec.degree)
        )
        convex_hull = ScipyConvexHullImpl(ra_dec_stack)
        convex_hull_vertices = ra_dec_stack[convex_hull.vertices]
        self.convex_hull_stcs = _polygon_vertices_to_stcs(convex_hull_vertices)

    def _show_catalog_with_optimization(self, *args):
        """
        If scatter marks for this catalog are currently shown, remove them and
        add a graphic overlay from the STC-S region of the convex hull vertices.

        If not specified, the color of the region will be the same as the scatter
        marks.
        """
        # no-op if the convex hull region has been drawn already:
        if self.overlay_info.get('type', '') == 'overlay_stcs':
            return

        # remove overlay if one is present (in this case, the overlay
        # would be a scatter overlay)
        self._remove_overlay()

        # add the convex hull region overlay
        overlay_options = dict(**self.catalog_options)

        # for available style options, see:
        # https://cds-astro.github.io/aladin-lite/global.html#GraphicOverlayOptions
        default_convex_hull_style = dict(
            color=self.catalog_options.get('color'),
            lineDash=[5, 10],
            lineWidth=6,
            fill=True,
            fillColor=self.catalog_options.get('color'),
            opacity=0.3,
        )

        for k, v in default_convex_hull_style.items():
            overlay_options.setdefault(k, v)

        self.overlay_info = self.mast_aladin.add_graphic_overlay_from_stcs(
            self.convex_hull_stcs,
            # display the catalog's name unmodified, don't show fraction of
            # sources visulaized:
            name=self.name,
            **overlay_options
        )
        self.n_sources_drawn = 0
