import re
import numpy as np
from scipy.spatial import ConvexHull as ScipyConvexHullImpl

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import MaskedColumn

__all__ = [
    "ConvexHull",
    "RandomSubset",
    "PriorityColumnSubset",
    "is_likely_an_observation_table",
    "PerformanceCatalog"
]


def is_likely_an_observation_table(table):
    """
    Returns True if ``table`` contains a column beginning with `"s_region"`.

    Parameters
    ----------
    table : `astropy.table.Table`
        Astropy table.

    Returns
    -------
    bool
    """
    return any(colname.lower().startswith('s_region') for colname in table.colnames)


class PerformanceCatalog:
    """
    Base class for source catalog overlays with optimization for
    large catalogs.

    Subclasses of `PerformanceCatalog` must:
    1. Implement a `__post_init__` method which contains any
    initialization tasks specific to the subclass.

    2. Implement a `_show_catalog_with_optimization` method which
    vizualizes the catalog sources within the viewport without
    plotting every source.

    3. `_show_catalog_with_optimization` must update the attribute with
    the number of sources drawn in the viewport,
    `~mast_aladin.catalogs.PerformanceCatalog.n_sources_drawn`.

    Peformance catalogs are not associated with an instance of `~mast_aladin.app.MastAladin`
    at initialization. After initialization, one must call
    `~mast_aladin.catalogs.PerformanceCatalog.attach_to_mast_aladin` to listen for updates
    to `~mast_aladin.app.MastAladin`'s viewport, and to trigger the first
    visualization of the source catalog in `~mast_aladin.app.MastAladin`.

    """
    overlay_info = {}

    def __init__(
            self,
            table,
            name=None,
            ra_column='RAJ2000',
            dec_column='DEJ2000',
            n_sources_max=5_000,
            **catalog_options
    ):
        """
        Parameters
        ----------
        table : `~astropy.table.Table`
            Source catalog.

        name : str, optional
            Name for the catalog layer. Default is "catalog".

        ra_column : str, optional
            Name of the column in `table` which specifies the RA coordinate for the
            scatter markers. Default: 'RAJ2000'.

        dec_column : str, optional
            Name of the column in `table` which specifies the Dec coordinate for the
            scatter markers. Default: 'DEJ2000'.

        n_sources_max : int, optional
            Maximum number of sources that can be displayed from this catalog in the
            viewport. The actual number will depend on the subclass, the catalog, and
            the viewport center and zoom. Default: 5_000.
        """
        self.table = table
        self.catalog_options = dict(**catalog_options)
        self.n_sources_max = n_sources_max
        self.n_sources_drawn = 0

        if name is None:
            self.name = 'catalog'

        self.name = name.strip()

        ra = table[ra_column]
        dec = table[dec_column]

        if isinstance(ra, MaskedColumn):
            ra = ra.filled(np.nan)
            dec = dec.filled(np.nan)

        self.source_coords = SkyCoord(ra=ra, dec=dec, unit=u.deg)
        self.__post_init__()

    def __post_init__(self):
        # implement in subclasses
        raise NotImplementedError

    def _show_catalog_with_optimization(self, *args):
        # implement in subclasses
        raise NotImplementedError

    def attach_to_mast_aladin(self, mast_aladin):

        """
        After `PerformanceCatalog` initialization, one must call
        `~mast_aladin.catalogs.PerformanceCatalog.attach_to_mast_aladin` to listen for updates
        to `~mast_aladin.app.MastAladin`'s viewport, and to trigger the first
        visualization of the source catalog in `~mast_aladin.app.MastAladin`.
        """
        # an instance of MastAladin
        self.mast_aladin = mast_aladin

        # trigger an update once on init to draw the catalog for the first time:
        self._on_viewport_update()

    def _polygon_vertices_to_stcs(self, vertices):
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

    @property
    def n_sources_in_viewport(self):
        """
        Number of catalog sources with coordinates that fall within the
        current viewport boundaries.

        Note: for some performance layers, this number will exceed the maximum
        number actually shown.
        """
        viewport = self.mast_aladin.get_viewport_region()
        sources_in_viewport = viewport.contains(self.source_coords, self.mast_aladin.wcs)
        return np.count_nonzero(sources_in_viewport)

    def _remove_overlay(self):
        overlay_names = [
            dict(
                basename=self._remove_source_count_from_name(fullname),
                fullname=fullname
            ) for fullname in self.mast_aladin.overlays
        ]
        for names in overlay_names:
            if names['basename'] == self.name:
                self.mast_aladin.remove_overlay(names['fullname'])
                break

    def _show_catalog_without_optimization(self, sources_in_viewport):
        """
        Show sources in the viewport "without optimization," meaning
        that all sources *in the viewport* are displayed. However, note that
        this method more memory efficient than the standard `Aladin.add_table`
        because only the sources in the viewport are added to
        `~mast_aladin.app.MastAladin`.

        Parameters
        ----------
        sources_in_viewport : boolean array
            Boolean mask with same length as `PerformanceCatalog.table` that is
            True for sources within the viewport.
        """
        # if the viewport has changed and few enough sources
        # will be visible, find and remove any catalog or stcs_region
        # overlays, then add back the table of visible sources
        self._remove_overlay()

        self.n_sources_drawn = np.count_nonzero(sources_in_viewport)

        # prevent redrawing an existing catalog:
        # if self.append_source_count_to_name(sources_in_viewport) in self.mast_aladin.overlays:
        #     return

        self.overlay_info = self.mast_aladin.add_table(
            self.table[sources_in_viewport],
            name=self._append_source_count_to_name(sources_in_viewport),
            performance_catalog=False,  # prevents performance layer checks
            **self.catalog_options
        )

    def _on_viewport_update(self, msg={}):
        """
        Triggered on changes to the viewport position, zoom, rotation, and aspect ratio.
        Updates the performance catalog visualization given the number of sources in the
        viewport.

        Parameters
        ----------
        msg : dict, optional
            Message from traitlet change.
        """
        viewport = self.mast_aladin.get_viewport_region()
        sources_in_viewport = viewport.contains(self.source_coords, self.mast_aladin.wcs)
        n_sources = np.count_nonzero(sources_in_viewport)

        overlay_names = [
            self._remove_source_count_from_name(name) for name in self.mast_aladin.overlays
        ]
        if self.name not in overlay_names and self.overlay_info:
            # catalog was once shown, but has since been removed from aladin
            return

        if n_sources < self.n_sources_max:
            # if the viewport has changed and few enough sources will be visible,
            self._show_catalog_without_optimization(sources_in_viewport)
        else:
            # if the viewport contains too many sources
            self._show_catalog_with_optimization(sources_in_viewport)

    def _remove_source_count_from_name(self, name):
        """
        Remove the source count suffix applied to performance catalog names
        in `~mast_aladin.app.MastAladin` when a subset of sources are shown.

        For example, if a catalog with name `Gaia` has been added and
        1000 out of the 5000 total sources are in the viewport, the catalog layer
        name in the Aladin overlays menu will appear as `"Gaia [1000/5000]"`. This
        regex method will strip the suffix and return `"Gaia"`. If the name contains
        no suffix, it is returned unchanged.

        Parameters
        ----------
        name : str
            Name of the catalog as it appears in the Aladin overlays menu,
            like `"Gaia [1000/5000]"`.

        Returns
        -------
        basename : str
            Name of the catalog without the source count suffix, like `"Gaia"`.
        """
        return re.sub(r'\s*\[\d+/\d+\]$', '', name)

    def _append_source_count_to_name(self, sources_in_viewport):
        """
        Append a source count suffix to a performance catalog name
        in `~mast_aladin.app.MastAladin` when a subset of sources are shown.

        For example, if a catalog with name `Gaia` has been added and
        1000 out of the 5000 total sources are in the viewport, this method
        returns  `"Gaia [1000/5000]"`. If the viewport contains all sources,
        no suffix is appended.

        Parameters
        ----------
        sources_in_viewport : boolean array
            Boolean mask with same length as `PerformanceCatalog.table` that is
            True for sources within the viewport.

        Returns
        -------
        basename : str
            Name of the catalog without the source count suffix, like `"Gaia"`.
        """
        n_sources_total = sources_in_viewport.size
        if self.n_sources_drawn == n_sources_total:
            return self.name
        return f"{self.name} [{self.n_sources_drawn}/{n_sources_total}]"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} (n={len(self.table)})>"


class ConvexHull(PerformanceCatalog):
    """
    Visualize a source catalog as scatter marks up to some number of points `n_sources_max`.
    For `>n_sources_max` sources, swap out the scatter marks for a region representing a
    polygon that connects the outermost catalog coordinates (the convex hull).

    Compute the convex hull with `~scipy.spatial.ConvexHull`
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
        self.convex_hull_stcs = self._polygon_vertices_to_stcs(convex_hull_vertices)

    def _show_catalog_with_optimization(self, *args):
        """
        If scatter marks for this catalog are currently shown, remove them and
        add a graphic overlay from the STC-S region of the convex hull vertices.

        If not specified, the color of the region will be the same as the scatter
        marks.
        """
        # add the convex hull *only* if the STC-S overlay isn't already displayed:
        if self.overlay_info.get('type', '') != 'overlay_stcs':

            # remove overlay if one is present:
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
                # omit the number of sources in the name a region graphic overlay:
                name=self.name,
                **overlay_options
            )
            self.n_sources_drawn = 0


class RandomSubset(PerformanceCatalog):
    """
    Visualize a source catalog as scatter marks up to some number of points `n_sources_max`.
    For `>n_sources_max` sources, only display a randomly selected subset of N sources
    within the viewport.
    """
    def __post_init__(self):
        self.rng = np.random.default_rng(seed=0)

    def _show_catalog_with_optimization(self, sources_in_viewport):
        """
        Randomly select up to `n_sources_max` sources from the sources
        contained within the viewport.
        """
        # remove catalog overlay if one is present:
        self._remove_overlay()

        # convert boolean mask to an array index (integer) mask:
        indices_in_viewport = np.flatnonzero(sources_in_viewport)

        random_sources_in_viewport = self.rng.choice(
            indices_in_viewport,
            size=self.n_sources_max,
            replace=False
        )
        # update before calling `add_table` so `add_source_count_to_name` works
        self.n_sources_drawn = random_sources_in_viewport.size

        self.overlay_info = self.mast_aladin.add_table(
            self.table[random_sources_in_viewport],
            name=self._append_source_count_to_name(sources_in_viewport),
            performance_catalog=False,
            **self.catalog_options
        )


class PriorityColumnSubset(PerformanceCatalog):
    """
    Visualize a source catalog as scatter marks up to some number of points `n_sources_max`.
    For `>n_sources_max` sources, only display N marks based on their values in
    the ``table`` column ``priority_column``.

    If `small_value_high_priority`, the smallest values in `priority_column` are
    given the highest priority. For example, you might use `small_value_high_priority=True`
    to prioritize the brightest sources if `priority_column` is a magnitude.
    """

    def __init__(
            self,
            table,
            name=None,
            ra_column='RAJ2000',
            dec_column='DEJ2000',
            n_sources_max=5_000,
            priority_column_name=None,
            small_value_high_priority=True,
            **catalog_options
    ):
        """
        Parameters
        ----------
        table : `~astropy.table.Table`
            Source catalog.

        name : str, optional
            Name for the catalog layer. Default is "catalog".

        ra_column : str, optional
            Name of the column in `table` which specifies the RA coordinate for the
            scatter markers. Default: 'RAJ2000'.

        dec_column : str, optional
            Name of the column in `table` which specifies the Dec coordinate for the
            scatter markers. Default: 'DEJ2000'.

        n_sources_max : int, optional
            Maximum number of sources that can be displayed from this catalog in the
            viewport. The actual number will depend on the catalog, and
            the viewport center and zoom. Default: 5_000.

        priority_column_name : str, required
            Prioritize which sources are shown using the column in `table` with name
            `priority_column_name`.

        small_value_high_priority : bool, optional
            If True, up to `n_sources_max` sources will be shown at a time, choosing sources
            with  the smallest values in the `table` column `priority_column_name`. For
            example, you might use `small_value_high_priority=True` to show the
            brightest `n_sources_max` sources if `table[priority_column_name]` is a magnitude.
        """
        if priority_column_name is None:
            raise ValueError(
                f"{self.__class__.__name__} must be initialized with a value for the keyword "
                "argument `priority_column_name`."
            )

        self.priority_column_name = priority_column_name
        self.small_value_high_priority = small_value_high_priority

        super().__init__(
            table,
            name=name,
            ra_column=ra_column,
            dec_column=dec_column,
            n_sources_max=n_sources_max,
            **catalog_options
        )

    def __post_init__(self):
        pass

    def _show_catalog_with_optimization(self, sources_in_viewport):
        """
        Plot the `n_sources_max` sources with the highest priority
        values in `table[priority_column_table]`. E.g., if
        `small_value_high_priority = True`, plots the `n_sources_max`
        smallest values.
        """
        # remove catalog overlay if one is present:
        self._remove_overlay()

        # convert boolean mask to an array index (integer) mask:
        indices_in_viewport = np.flatnonzero(sources_in_viewport)
        priorities_in_viewport = np.asarray(
            self.table[self.priority_column_name][indices_in_viewport]
        )

        # `np.argpartition` finds the smallest `kth` values,
        # and returns the array with the smallest `kth` values placed
        # into the first `kth` entries of the output, without sorting the
        # rest of the array. This is more efficient than a full sort.
        if self.small_value_high_priority:
            top_priority_indices = np.argpartition(
                priorities_in_viewport, kth=self.n_sources_max
            )[:self.n_sources_max]
        else:
            # change the sign and slice for setting the highest value
            # with the highest priority:
            top_priority_indices = np.argpartition(
                priorities_in_viewport, kth=-self.n_sources_max
            )[-self.n_sources_max:]

        # update before calling `add_table` so `add_source_count_to_name` works
        self.n_sources_drawn = top_priority_indices.size

        self.overlay_info = self.mast_aladin.add_table(
            self.table[indices_in_viewport][top_priority_indices],
            name=self._append_source_count_to_name(sources_in_viewport),
            performance_catalog=False,
            **self.catalog_options
        )
