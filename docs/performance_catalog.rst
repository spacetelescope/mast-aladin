
Improve Aladin performance for large source catalogs
====================================================

The `~mast_aladin.app.MastAladin` method `~mast_aladin.app.MastAladin.add_table` 
can be used to add a source catalog to an Aladin instance. 
Pan and zoom operations in Aladin become less responsive when the number of sources
in the viewport exceeds ~10k. MAST users on the Roman Research Nexus can expect to
work frequently with source catalogs exceeding 10k sources.

To improve Aladin performance for large source catalogs, mast-aladin
provides implementations of "performance catalogs" via 
`~mast_aladin.catalogs.convex_hull_region.ConvexHullRegion` and 
`~mast_aladin.catalogs.priority_column_subset.PriorityColumnSubset`.
These visualizations enforce an upper limit on the number of sources
displayed from each catalog, set by the keyword argument 
``n_sources_max``. If the number of visible sources from a given catalog
exceeds ``n_sources_max``, `~mast_aladin.app.MastAladin` swaps in a more
performant visualization, depending on the class, as outlined below.

Performance catalogs
--------------------

Sources are represented as scatter marks in Aladin when
the number of visible catalog sources is smaller than ``n_sources_max``. 
Performance catalogs listen for changes in the Aladin viewport's center, zoom
level, and aspect ratio. When these properties change, mast-aladin re-evaluates
the number of sources within the viewport.

The `~ipyaladin.widget.Aladin` method `~ipyaladin.widget.Aladin.add_table` always
displays all sources as scatter marks within the viewport. `~mast_aladin.app.MastAladin`'s
`~mast_aladin.app.MastAladin.add_table` method has the same default behavior for 
source catalogs when less than ``n_sources_max`` sources are visible in the viewport (default: 5,000).
If more than ``n_sources_max`` sources fall within the viewport, `~mast_aladin.app.MastAladin`
visualizes the catalog using `~mast_aladin.catalogs.convex_hull_region.ConvexHullRegion`
by default.

To force all sources to be loaded at once, without using 
`~mast_aladin.catalogs.convex_hull_region.ConvexHullRegion`, set 
``performance_cls=None`` like this:

.. code-block:: python

    from mast_aladin import MastAladin

    mast_aladin = MastAladin()

    # to opt out of performance catalog visualizations:
    mast_aladin.add_table(source_catalog_table, performance_cls=None);


`~mast_aladin.catalogs.convex_hull_region.ConvexHullRegion`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the number of visible catalog sources is greater than ``n_sources_max``, 
mast-aladin removes the scatter marks and adds a filled polygon
to Aladin as a graphic overlay. This polygon is the convex hull of the source
coordinates -- which has vertices at the smallest set of sources which enclose
all other sources.

Let's show up to 5,000 sources as blue circle scatter marks from a Gaia source catalog
that we have fetched from Vizier, where the standard column names for RA and Dec are
``RAJ2000`` and ``DEJ2000``. When more than 5,000 sources fall within the viewport, remove the
scatter marks and show a region representing the convex hull of the source coordinates.

.. code-block:: python

    from mast_aladin import MastAladin
    from mast_aladin.catalogs import ConvexHullRegion

    mast_aladin = MastAladin()

    performance_catalog = ConvexHullRegion(
        source_catalog_table,
        name='Gaia',

        # performance viz config:
        n_sources_max=5_000,  # [default]
        ra_field='RAJ2000',  # [default]
        dec_field='DEJ2000', # [default]

        # marker settings:
        size=10,
        shape='circle',
        color='#0090ff',
    )

    mast_aladin.add_table(performance_catalog);

As mentioned above, `~mast_aladin.catalogs.convex_hull_region.ConvexHullRegion` is the
default performance catalog implementation in the `~mast_aladin.app.MastAladin` method
`~mast_aladin.app.MastAladin.add_table`, so one could get the same visualization by calling
`~mast_aladin.app.MastAladin.add_table` directly:

.. code-block:: python

    from mast_aladin import MastAladin

    mast_aladin = MastAladin()

    mast_aladin.add_table(
        table=source_catalog_table,
        name='Gaia',

        # performance viz config:
        n_sources_max=5_000,  # [default]
        ra_field='RAJ2000',  # [default]
        dec_field='DEJ2000', # [default]

        # marker settings:
        size=10,
        shape='circle',
        color='#0090ff',
    );

`~mast_aladin.catalogs.priority_column_subset.PriorityColumnSubset`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the number of visible catalog sources is greater than ``n_sources_max``, 
mast-aladin shows only the ``n_sources_max`` "top priority" sources. The 
priority values come from one of the source catalog's table columns. For example, 
to plot the brightest ``n_sources_max`` sources a Gaia source catalog based on 
their values in the ``"Gmag"`` column:

.. code-block:: python


    from mast_aladin import MastAladin
    from mast_aladin.catalogs import PriorityColumnSubset

    mast_aladin = MastAladin()

    performance_catalog = PriorityColumnSubset(
        source_catalog_table,
        name='Gaia',

        # viz config:
        n_sources_max=1_000,
        ra_field='RAJ2000',
        dec_field='DEJ2000',
        priority_column_name='Gmag',
        small_value_high_priority=True,

        # marker settings:
        size=10,
        shape='circle',
        color='#ff0000',
    )

To plot the brightest sources, we set ``small_value_high_priority = True`` since
smaller magnitudes are brighter stars, and we choose to give those sources
top priority. If you only had the flux in the G band ``"FG"`` instead of the magnitude, 
you could get the same visualization by setting:

.. code-block:: python

    ...
    priority_column_name="FG",
    small_value_high_priority=False,
    ...


Define your own performant catalog visualization
------------------------------------------------

Users can build their own performant catalog visualization strategies by 
subclassing `~mast_aladin.catalogs.performance.PerformanceCatalog`. 

Subclasses of `~mast_aladin.catalogs.performance.PerformanceCatalog` must
meet the following requirements:

    1. Implement a ``__post_init__`` method which contains any
    initialization tasks specific to the subclass.

    2. Implement a ``_show_catalog_with_optimization`` method which
    vizualizes the catalog sources within the viewport with some
    performance improvement over plotting every source.

    3. ``_show_catalog_with_optimization`` must update the attribute with
    the number of sources drawn in the viewport,
    ``PerformanceCatalog.n_sources_drawn``.

Below is an example performance catalog implementation that plots up to ``n_sources_max``
*random* sources from within the viewport. This isn't meant to be a practical performance
catalog, but rather an example for illustrative purposes:

.. code-block:: python

    import numpy as np
    from mast_aladin.catalogs import PerformanceCatalog

    class RandomSubset(PerformanceCatalog):
        """
        Visualize a source catalog as scatter marks up to some number
        of points `n_sources_max`. For `>n_sources_max` sources, only
        display a randomly selected subset of N sources within the
        viewport.
        """
        def __post_init__(self):
            # add a class attribute for a random number generator
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

            # select ``n_sources_max`` random sources from within the viewport
            random_sources_in_viewport = self.rng.choice(
                indices_in_viewport,
                size=self.n_sources_max,
                replace=False
            )
            # update `n_sources_drawn` before calling `add_table`, so the
            # `add_source_count_to_name` method works as intended:
            self.n_sources_drawn = random_sources_in_viewport.size

            self.overlay_info = self.mast_aladin.add_table(

                # add only the randomly selected sources from the viewport:
                self.table[random_sources_in_viewport],

                # label the Aladin overlay with the catalog name and the 
                # number of sources visible within the viewport, over the
                # total, like "Gaia [5000/93257]".
                name=self._append_source_count_to_name(sources_in_viewport),

                # since this method defines how to visualize a subset or summary 
                # of the full source catalog, we set `performance_cls=None` to ensure
                # no other performance catalog will be applied to these sources:
                performance_cls=None,
                **self.catalog_options
            )


Note: peformance catalogs are not associated with an instance of `~mast_aladin.app.MastAladin`
at initialization. After initialization, one must call
``PerformanceCatalog._attach_to_mast_aladin`` to
listen for updates to `~mast_aladin.app.MastAladin`'s viewport, and to trigger
the first visualization of the source catalog in `~mast_aladin.app.MastAladin`.
``PerformanceCatalog._attach_to_mast_aladin`` is called within
`~mast_aladin.app.MastAladin.add_table`.
