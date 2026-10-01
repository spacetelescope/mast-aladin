import numpy as np
from .performance import PerformanceCatalog


class PriorityColumnSubset(PerformanceCatalog):
    """
    Visualize a source catalog as scatter marks up to some number of
    points ``n_sources_max``. For ``>n_sources_max`` sources, only
    display ``n_sources_max`` marks based on the source catalog's ``table``
    column ``priority_column``.

    If ``small_value_high_priority``, the smallest values in
    ``priority_column`` are given the highest priority. For example, you
    might use ``small_value_high_priority=True`` to prioritize the
    brightest sources if ``priority_column`` is a magnitude.
    """

    def __init__(
            self,
            table,
            *,

            # required keyword arguments:
            priority_column_name,
            small_value_high_priority,

            # optional keyword arguments:
            name=None,
            ra_field='RAJ2000',
            dec_field='DEJ2000',
            n_sources_max=5_000,
            **catalog_options
    ):
        """
        Parameters
        ----------

        priority_column_name : str, required
            Prioritize which sources are shown using the column in `table` with name
            `priority_column_name`.

        small_value_high_priority : bool, required
            If True, up to ``n_sources_max`` sources will be shown at a time, choosing
            sources with the smallest values in the ``table`` column ``priority_column_name``.
            For example, you might use ``small_value_high_priority = True`` to show the
            brightest ``n_sources_max`` sources if ``table[priority_column_name]``
            is a magnitude.

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
            viewport. The actual number will depend on the catalog, and
            the viewport center and zoom. Default: 5_000.
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
            ra_field=ra_field,
            dec_field=dec_field,
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
            name=self._name_with_source_count(sources_in_viewport),
            performance_catalog=False,
            **self.catalog_options
        )
