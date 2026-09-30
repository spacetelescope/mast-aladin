import re
from abc import ABC, abstractmethod

import numpy as np

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import MaskedColumn


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


class PerformanceCatalog(ABC):
    """
    Abstract base class for source catalog overlays with
    optimization for large catalogs. This class is not meant to
    be initialized by users.

    Subclasses of `PerformanceCatalog` must:
    1. Implement a ``__post_init__`` method which contains any
    initialization tasks specific to the subclass.

    2. Implement a ``_show_catalog_with_optimization`` method which
    vizualizes the catalog sources within the viewport without
    plotting every source.

    3. ``_show_catalog_with_optimization`` must update the attribute
    with the number of sources drawn in the viewport,
    ``PerformanceCatalog.n_sources_drawn``.

    Peformance catalogs are not associated with an instance of
    `~mast_aladin.app.MastAladin` at initialization. After
    initialization, one must call
    `~mast_aladin.catalogs.PerformanceCatalog._attach_to_mast_aladin`
    to listen for updates to the viewport in `~mast_aladin.app.MastAladin`,
    and to trigger the first visualization of the source catalog
    in `~mast_aladin.app.MastAladin`. The attach method is called within
    `~mast_aladin.app.MastAladin.add_table`.

    """
    overlay_info = {}
    _last_viewport_region_vertices = None
    _last_source_indices_in_viewport = None

    def __init__(
            self,
            table,
            name=None,
            ra_field='RAJ2000',
            dec_field='DEJ2000',
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

        ra_field : str, optional
            Name of the column in `table` which specifies the RA coordinate for the
            scatter markers. Default: 'RAJ2000'.

        dec_field : str, optional
            Name of the column in `table` which specifies the Dec coordinate for the
            scatter markers. Default: 'DEJ2000'.

        n_sources_max : int, optional
            Maximum number of sources that can be displayed from this catalog in the
            viewport. The actual number will depend on the subclass, the catalog, and
            the viewport center and zoom. Default: 5_000.
        """
        self.ra_field = ra_field
        self.dec_field = dec_field
        self.table = table
        self.catalog_options = dict(**catalog_options)
        self.n_sources_max = n_sources_max

        self.n_sources_drawn = 0

        if name is None:
            self.name = 'catalog'

        self.name = name.strip()

        for col, name in [[ra_field, 'RA'], [dec_field, 'Dec']]:
            if col not in table.colnames:
                raise ValueError(f"{name} column '{col}' not found in table.")

        ra = table[ra_field]
        dec = table[dec_field]

        if isinstance(ra, MaskedColumn):
            ra = ra.filled(np.nan)
            dec = dec.filled(np.nan)

        self.source_coords = SkyCoord(ra=ra, dec=dec, unit=u.deg)
        self.__post_init__()

    @abstractmethod
    def __post_init__(self):
        # implement in subclasses
        raise NotImplementedError

    @abstractmethod
    def _show_catalog_with_optimization(self, *args):
        # implement in subclasses
        raise NotImplementedError

    def _attach_to_mast_aladin(self, mast_aladin):
        """
        After `PerformanceCatalog` initialization, one must call
        `~mast_aladin.catalogs.performance.PerformanceCatalog._attach_to_mast_aladin`
        to listen for updates to `~mast_aladin.app.MastAladin`'s viewport, and to
        trigger the first visualization of the source catalog in
        `~mast_aladin.app.MastAladin`.

        Parameters
        ----------
        mast_aladin : `~mast_aladin.app.MastAladin`
            Instance of `MastAladin`.
        """
        # an instance of MastAladin
        self.mast_aladin = mast_aladin

        # trigger an update once on init to draw the catalog for the first time:
        self._on_viewport_update()

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
        """
        Get the names of overlays in the Aladin overlay menu, remove source counts from
        names if present, remove any layer with a name that matches `self.name`.
        """
        overlay_names = [
            dict(
                basename=self._remove_source_count_from_name(fullname),
                fullname=fullname
            ) for fullname in self.mast_aladin.overlays
        ]
        for names in overlay_names:
            if names['basename'] == self.name:
                self.mast_aladin.remove_overlay(names['fullname'])

                # assume there's only one overlay to find, break here:
                break

    def _show_catalog_without_optimization(self, sources_in_viewport):
        """
        Show sources in the viewport "without optimization," meaning
        that all sources *in the viewport* are displayed. However, note that
        this method is more memory efficient than the standard `Aladin.add_table`
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

        self.overlay_info = self.mast_aladin.add_table(
            self.table[sources_in_viewport],
            name=self._name_with_source_count(sources_in_viewport),
            performance_cls=None,  # prevents another performance catalog from being applied
            ra_field=self.ra_field,
            dec_field=self.dec_field,
            **self.catalog_options
        )

    def _on_viewport_update(self, msg={}, redraw_relative_separation=0.01):
        """
        Triggered on changes to the viewport position, zoom, rotation, and aspect ratio.
        Updates the performance catalog visualization given the number of sources in the
        viewport.

        Several checks are done before redrawing a catalog on viewport udpates:

        1. On each call, the coordinates of the current viewport corners are compared to the
        previous `_on_viewport_update` call. If the coordinates are identical, don't redraw
        the catalog.

        2. If the change in the corners is very small, don't redraw the catalog. The tolerance is
        defined as the maximum separation between the old and new corner coordinates in
        units of the viewport's span in right ascension, set by `redraw_relative_separation`.

        3. If the corners have shifted by more than the maximum tolerance in step (2), check which
        sources from the catalog are now visible within the viewport. If visible sources
        do not change after the viewport update, do not redraw.

        4. Otherwise, redraw.

        Parameters
        ----------
        msg : dict, optional
            Message from traitlet change.
        """
        viewport = self.mast_aladin.get_viewport_region()

        if self._last_viewport_region_vertices is None:
            # on the first call, save the viewport corners and visible source indices
            self._last_viewport_region_vertices = viewport.vertices.copy()
            sources_in_viewport = viewport.contains(
                self.source_coords,
                self.mast_aladin.wcs
            )
            source_indices_in_viewport = np.flatnonzero(sources_in_viewport)
            self._last_source_indices_in_viewport = source_indices_in_viewport.copy()

        elif np.any(viewport.vertices != self._last_viewport_region_vertices):
            # the viewport has moved.

            # now we check if it's moved more than the threshold for redrawing
            # the catalog, which is the separation between the old and new
            # catalog coordinates, normalized by the viewport's span in RA:
            corner_separation = viewport.vertices.separation(
                self._last_viewport_region_vertices
            )
            ra_span = np.ptp(np.concatenate([
                viewport.vertices.ra,
                self._last_viewport_region_vertices.ra
            ]))

            if np.all(corner_separation / ra_span < redraw_relative_separation):
                # if the viewport has moved <redraw_relative_separation of the
                # viewport's span in RA, don't update the performance catalog
                return

            else:
                # At this step, the viewport has moved by more than the required
                # separation to trigger a redraw. Now check if the number of visible
                # sources has changed.
                sources_in_viewport = viewport.contains(
                    self.source_coords,
                    self.mast_aladin.wcs
                )
                source_indices_in_viewport = np.flatnonzero(sources_in_viewport)

                if (
                    source_indices_in_viewport.size ==
                    self._last_source_indices_in_viewport.size
                ) and np.all(
                    source_indices_in_viewport ==
                    self._last_source_indices_in_viewport
                ):
                    # The same sources are visible before and after, don't update
                    return
                else:
                    # Save the viewport stats, and continue below to redraw the catalog:
                    self._last_source_indices_in_viewport = source_indices_in_viewport.copy()
                    self._last_viewport_region_vertices = viewport.vertices.copy()

        else:
            # the viewport hasn't changed, don't update the performance catalog
            return

        n_sources = np.count_nonzero(sources_in_viewport)

        overlay_names = [
            self._remove_source_count_from_name(name)
            for name in self.mast_aladin.overlays
        ]
        if self.name not in overlay_names and self.overlay_info:
            # Catalog was once shown, but has since been removed from aladin.

            # Remove the performance catalog from `MastAladin.performance_catalogs`:
            for performance_catalog in self.mast_aladin.performance_catalogs:
                if performance_catalog.name == self.name:
                    self.mast_aladin.performance_catalogs.remove(
                        performance_catalog
                    )
                    break

            # exit here:
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

    def _name_with_source_count(self, sources_in_viewport):
        """
        Return the catalog name with a source count suffix when a subset
        of sources are shown.

        For example, if a catalog with name ``Gaia`` has been added and
        1000 out of the 5000 total sources are in the viewport, this method
        returns  ``"Gaia [1000/5000]"``. If the viewport contains all sources,
        no source count is appended.

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
