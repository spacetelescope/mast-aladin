import warnings
import numpy as np
from scipy.spatial import ConvexHull as ScipyConvexHullImpl
from .performance import PerformanceCatalog


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
        convex_hull_vertices = convex_hull_on_sphere(
            ra=self.source_coords.ra.degree,
            dec=self.source_coords.dec.degree
        )
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


def convex_hull_on_sphere(ra, dec):
    """
    Compute the convex hull for points on a sphere, given spherical
    coordinates.

    This approach works for catalogs near a meridian or
    the poles. This approach does *not* work if the coordinates span
    more than one hemisphere -- in this case a warning is raised.

    Procedure:

    1. convert spherical (lon, lat) -> cartesian coordinates (x, y, z)
    2. apply rotation matrices R_z, R_y to the cartesian coordinates
       (x, y, z) to translate the source coordinates to a new cartesian
       frame (x', y', z') such that (x_mean, y_mean) -> (x', y') = (0, 0)
    3. Compute the ordinary convex hull on the (x', y') coordinates

    Parameters
    ----------
    ra : float [degrees]
        Right ascension
    dec : float [degrees]
        Declination

    Returns
    -------
    vertices : array of ints
        Indices from the ``ra`` and ``dec`` arrays that define the vertices
        of the convex hull.
    """
    # define longitude (aka phi) and colatitude (aka theta) from RA and Dec:
    lon = np.radians(ra)
    colat = np.radians(90 - dec)  # colatitude, a.k.a. the polar angle

    # convert polar coordinates to cartesian:
    x = np.sin(colat) * np.cos(lon)
    y = np.sin(colat) * np.sin(lon)
    z = np.cos(colat)
    cartesian = np.array([x, y, z])

    # the mean coordinate in cartesian coordinates gives the
    # geometric center of the catalog:
    x_center, y_center, z_center = np.array([
        c.mean() for c in cartesian
    ])

    # translate the cartesian geometric center back to spherical coords:
    lon_center = np.arctan2(y_center, x_center)
    colat_center = np.arccos(z_center)

    # de-rotate the coordinate system (x, y, z) so the geometric center
    # is rotated to (x', y') = (0, 0):
    cartesian_centered = R_y(-colat_center) @ R_z(-lon_center) @ cartesian

    # warn the user if the source coordinates span >1 hemisphere:
    z_centered = cartesian_centered[-1]
    if np.any(z_centered > 0) and np.any(z_centered < 0):
        msg = (
            "The convex hull calculated for this catalog will be spurious "
            "because the catalog coordinates are distributed across more "
            "than one hemisphere. Consider an alternative performance catalog "
            "visualization like PriorityColumnSubset."
        )
        warnings.warn(msg, UserWarning)

    # compute the convex hull from (x', y')
    hull = ScipyConvexHullImpl(cartesian_centered[:2].T)
    return np.column_stack([
        ra[hull.vertices],
        dec[hull.vertices]
    ])


def R_y(theta):
    """
    3D cartesian rotation matrix about the y-axis for
    an angle theta [radians].
    """
    return np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)],
    ])


def R_z(theta):
    """
    3D cartesian rotation matrix about the z-axis for
    an angle theta [radians].
    """
    return np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])
