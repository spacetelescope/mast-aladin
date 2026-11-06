Getting started
---------------

Launch mast-aladin
^^^^^^^^^^^^^^^^^^

To open `~mast_aladin.app.MastAladin` from a notebook in 
`Jupyter Lab <https://jupyterlab.readthedocs.io/en/latest/>`_, run:

.. code-block:: python

    from mast_aladin import MastAladin

    mast_aladin = MastAladin(
        target='83.82 -5.3875',  # Orion Nebula
        fov=3                    # Set field of view to 3 degrees
    )

    # open mast-aladin in a sidecar
    mast_aladin.show()


.. image:: https://github.com/spacetelescope/widget-docs/blob/main/mast-aladin/getting_started/cell0.jpg?raw=true
    :width: 70%
    :align: center

|

By default, `~mast_aladin.app.MastAladin.show` will display the widget in a 
`Jupyter Lab sidecar <https://github.com/jupyter-widgets/jupyterlab-sidecar>`_
to the right of the Jupyter notebook.


Search MAST for observations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, let's search for 100 JWST observations within the field of view using
`~mast_aladin.app.MastAladin.search_this_area` and plot the observation
footprints in red: 

.. code-block:: python

    observations, overlay = mast_aladin.search_this_area(
        mission='jwst',  # search for JWST observations
        limit=100        # limit response to the first N results
    )

    # set the color of the footprint overlays:
    overlay.update(color='#ff0000')


.. image:: https://github.com/spacetelescope/widget-docs/blob/main/mast-aladin/getting_started/cell1.jpg?raw=true
    :width: 70%
    :align: center

|

The MAST query result is saved to ``observations``, which is an astropy `~astropy.table.Table`:

.. code-block:: python

    >>> observations

    ArchiveFileID           fileSetName            productLevel  ... access cal_ver       ang_sep      
    ------------- ------------------------------- -------------- ... ------ ------- -------------------
        257727030        jw01256-o001_t001_nircam              3 ... PUBLIC   3.0.0                 0.0
        257595556        jw01256-o002_t001_nircam              3 ... PUBLIC   3.0.0                 0.0
        264555855 jw02770-o001_b000000014_nirspec         2bs, 3 ... PUBLIC   3.0.0                 0.0
        265439071 jw02770-o001_b000000067_nirspec         2bs, 3 ... PUBLIC   3.0.0                 0.0
        267355456 jw02770-o001_b000000036_nirspec         2bs, 3 ... PUBLIC   3.0.0                 0.0
        258033265        jw01288-o001_t011_nircam              3 ... PUBLIC   3.0.0 0.10563621666666667
        267561750 jw02770-o001_b000000071_nirspec         2bs, 3 ... PUBLIC   3.0.0 0.17267581666666668
        263175722       jw01228003001_02101_00002     1b, 2a, 2b ... PUBLIC   3.0.0 0.31410466666666664
        263175725       jw01228003001_02101_00001     1b, 2a, 2b ... PUBLIC   3.0.0           0.3185939
        263175711       jw0-u 1228003001_02101_00003     1b, 2a, 2b ... PUBLIC   3.0.0  0.3196436166666667
            ...                             ...            ... ...    ...     ...                 ...
        256799703       jw01256001002_02105_00003 1b, 2a, 2b, 2c ... PUBLIC   3.0.0  1.7430215999999998
        256798751       jw01256001002_02109_00003 1b, 2a, 2b, 2c ... PUBLIC   3.0.0           1.7430279
        256801120       jw01256001002_02101_00003 1b, 2a, 2b, 2c ... PUBLIC   3.0.0  1.7430379333333332
        256800731       jw01256001002_02103_00003 1b, 2a, 2b, 2c ... PUBLIC   3.0.0  1.7430635166666666
        256797928       jw01256001003_02101_00003 1b, 2a, 2b, 2c ... PUBLIC   3.0.0  1.7746291166666666
        256798054       jw01256001003_02103_00003 1b, 2a, 2b, 2c ... PUBLIC   3.0.0  1.7746893666666668
        267556549 jw02770-o001_b000000013_nirspec         2bs, 3 ... PUBLIC   3.0.0           1.7991833
        258266520         jw01288-c1004_t010_miri              3 ... PUBLIC   3.0.0  1.8248612333333334
        258109099          jw01288-o002_t010_miri              3 ... PUBLIC   3.0.0  1.8248612333333334
        256799291       jw01256001002_02107_00004 1b, 2a, 2b, 2c ... PUBLIC   3.0.0          1.84088835
    Length = 100 rows

Clicking on the edge of a footprint will reveal the observation query result
information in the mast-aladin widget:

.. image:: https://github.com/spacetelescope/widget-docs/blob/main/mast-aladin/getting_started/cell1-click.jpg?raw=true
    :width: 70%
    :align: center

|


Using astroquery
^^^^^^^^^^^^^^^^

For fully-configurable MAST Mission Searches, use `astroquery.mast.missions.MastMissionsClass`,
for details see the `astroquery.mast documentation 
<https://docs.astropy.org/projects/astroquery/en/latest/mast/mast_missions.html>`_.
The code below reproduces the query above:

.. code-block:: python

    from astroquery.mast import MastMissions

    mission_search = MastMissions(mission='jwst')
    observations = mission_search.query_region(
        coordinates=mast_aladin.target,
        radius='30 arcmin',
        limit=100
    )

Note: Mission Search supports cone searches with radii up to 30 arcmin. The mast-aladin 
field of view in this example is significantly wider, so results are returned within 
30 arcmin of the center of the field of view.

To plot the observation footprints from Mission Search query results, use
`~mast_aladin.app.MastAladin.add_table`:

.. code-block:: python

    mast_aladin.add_table(observations)

