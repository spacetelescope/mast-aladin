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
    Returns True if ``table`` does not contain an 's_region' column.

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

    def attach_to_mast_aladin(self, mast_aladin):
        # to be called by MastAladin.add_table to attach this catalog to
        # an instance of MastAladin
        self.mast_aladin = mast_aladin

        # trigger an update once on init to draw the catalog for the first time:
        self.on_viewport_update()

    def __post_init__(self):
        # implement in subclasses
        raise NotImplementedError

    def polygon_vertices_to_stcs(self, vertices):
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

    def remove_overlay(self):
        overlay_names = [
            dict(
                basename=self.remove_source_count_from_name(fullname),
                fullname=fullname
            ) for fullname in self.mast_aladin.overlays
        ]
        for names in overlay_names:
            if names['basename'] == self.name:
                self.mast_aladin.remove_overlay(names['fullname'])
                break

    def show_catalog_without_optimization(self, sources_in_viewport):
        # if the viewport has changed and few enough sources
        # will be visible, find and remove any catalog or stcs_region
        # overlays, then add back the table of visible sources
        self.remove_overlay()

        self.n_sources_drawn = np.count_nonzero(sources_in_viewport)

        # prevent redrawing an existing catalog:
        # if self.name_with_source_count(sources_in_viewport) in self.mast_aladin.overlays:
        #     return

        self.overlay_info = self.mast_aladin.add_table(
            self.table[sources_in_viewport],
            name=self.name_with_source_count(sources_in_viewport),
            performance_catalog=False,  # prevents performance layer checks
            **self.catalog_options
        )

    def show_catalog_with_optimization(self, *args):
        # implement in subclasses
        raise NotImplementedError

    def on_viewport_update(self, msg={}):
        viewport = self.mast_aladin.get_viewport_region()
        sources_in_viewport = viewport.contains(self.source_coords, self.mast_aladin.wcs)
        n_sources = np.count_nonzero(sources_in_viewport)

        overlay_names = [
            self.remove_source_count_from_name(name) for name in self.mast_aladin.overlays
        ]
        if self.name not in overlay_names and self.overlay_info:
            # catalog was once shown, but has since been removed from aladin
            return

        if n_sources < self.n_sources_max:
            # if the viewport has changed and few enough sources will be visible,
            self.show_catalog_without_optimization(sources_in_viewport)
        else:
            # if the viewport contains too many sources
            self.show_catalog_with_optimization(sources_in_viewport)

    def remove_source_count_from_name(self, name):
        return re.sub(r'\s*\[\d+/\d+\]$', '', name)

    def name_with_source_count(self, sources_in_viewport):
        n_sources_total = sources_in_viewport.size
        if self.n_sources_drawn == n_sources_total:
            return self.name
        return f"{self.name} [{self.n_sources_drawn}/{n_sources_total}]"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} (n={len(self.table)})>"


class ConvexHull(PerformanceCatalog):
    """
    Visualize a source catalog as scatter marks up to some number of points N.
    For >N sources, swap out the scatter marks for a region representing the
    convex hull of the catalog.
    """
    def __post_init__(self):

        ra_dec_stack = np.column_stack(
            (self.source_coords.ra.degree, self.source_coords.dec.degree)
        )
        convex_hull = ScipyConvexHullImpl(ra_dec_stack)
        self.convex_hull_vertices = ra_dec_stack[convex_hull.vertices]
        self.convex_hull_stcs = self.polygon_vertices_to_stcs(self.convex_hull_vertices)

    def show_catalog_with_optimization(self, *args):
        # add the convex hull *only* if the STC-S overlay isn't already displayed:
        if self.overlay_info.get('type', '') != 'overlay_stcs':

            # remove overlay if one is present:
            self.remove_overlay()

            # add the convex hull region overlay
            overlay_options = dict(**self.catalog_options)

            # for available style options, see:
            # https://cds-astro.github.io/aladin-lite/global.html#GraphicOverlayOptions
            default_convex_hull_style = dict(
                color=self.catalog_options.get('color'),

                # low opacity fills via ipyaladin can be revisited once the following
                # issue is addressed: https://github.com/cds-astro/ipyaladin/issues/192
                lineDash=[5, 10],
                lineWidth=6,
                fill=True,
                fillColor=self.catalog_options.get('color'),
                opacity=0.3,
            )

            for k, v in default_convex_hull_style.items():
                overlay_options.setdefault(k, v)

            self.overlay_info = self.mast_aladin.add_graphic_overlay_from_stcs(
                self.convex_hull_stcs, name=self.name, **overlay_options
            )
            self.n_sources_drawn = 0


class RandomSubset(PerformanceCatalog):
    """
    Visualize a source catalog as scatter marks up to some number of points N.
    For >N sources, only display a randomly selected subset of N sources 
    within the viewport.
    """

    def __post_init__(self):
        self.rng = np.random.default_rng(seed=0)

    def show_catalog_with_optimization(self, sources_in_viewport):
        # remove catalog overlay if one is present:
        self.remove_overlay()

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
            name=self.name_with_source_count(sources_in_viewport),
            performance_catalog=False,
            **self.catalog_options
        )


class PriorityColumnSubset(PerformanceCatalog):
    """
    Visualize a source catalog as scatter marks up to some number of points N.
    For >N sources, only display N marks based on their values in
    the ``table`` column ``priority_column``.

    If ``small_value_high_priority``, the smallest values in ``priority_column`` are
    given the highest priority. For example, you might use ``small_value_high_priority=True``
    to prioritize the brightest sources if ``priority_column`` is a magnitude.
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

    def show_catalog_with_optimization(self, sources_in_viewport):
        # remove catalog overlay if one is present:
        self.remove_overlay()

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
            name=self.name_with_source_count(sources_in_viewport),
            performance_catalog=False,
            **self.catalog_options
        )
