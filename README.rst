.. |stsci-logo| image:: docs/assets/mast-aladin-logo.svg
    :alt: STScI logo
    :height: 200px

|stsci-logo|

.. image:: https://github.com/spacetelescope/mast-aladin/actions/workflows/ci_workflows.yml/badge.svg
    :target: https://github.com/spacetelescope/mast-aladin/actions/workflows/ci_workflows.yml
    :alt: GitHub Actions CI Status

.. image:: https://readthedocs.org/projects/mast-aladin/badge/?version=latest
    :target: https://mast-aladin.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status



``mast-aladin`` adds convenience methods for visualizing and interacting with query results from MAST on the Aladin sky atlas, including queries for observations and sources in catalogs. 

``mast-aladin`` is a Python package maintained by the Space Telescope Science Institute that extends `ipyaladin <https://github.com/cds-astro/ipyaladin>`_, a package maintained by CDS (Centre de Données astronomiques de Strasbourg). ``ipyaladin`` is a Jupyter widget wrapper for `aladin-lite <https://github.com/cds-astro/aladin-lite>`_, also maintained by CDS.

Key Features
------------

- Runs in Jupyter notebooks locally or on the `Roman Research Nexus <https://roman.science.stsci.edu/>`_.
- Provides interactive access through the Aladin Lite interface and a Python API, with all-sky imaging from surveys including SDSS, Pan-STARRS, WISE, GALEX, and more.
- Visualizes and interacts with MAST observation and catalog query results. Includes plotting observation footprints and source catalog plotting tools, and works with `mast-table <https://github.com/spacetelescope/mast-table>`_ results.
- Integrates with `jdaviz <https://jdaviz.readthedocs.io/en/stable/>`_ through the AIDA (Astronomical Interactive Data Analysis) framework.

Full Documentation
------------------

`Click here to see the full documentation for mast-aladin 
on Read The Docs <https://mast-aladin.readthedocs.io/en/latest/>`_.

Quick Start
-----------

Installing
^^^^^^^^^^
You can install the latest stable release version of ``mast-aladin`` using pip:

.. code-block:: bash

   pip install mast-aladin --upgrade

Or, you can install the latest development version of ``mast-aladin`` using pip:

.. code-block:: bash

   pip install git+https://github.com/spacetelescope/mast-aladin --upgrade

Installing ``mast-aladin`` in a new virtual or conda environment will help you to avoid 
version conflicts with other packages you may have installed, for example:

.. code-block:: bash

   conda create -n mast-aladin-env python=3.12
   conda activate mast-aladin-env
   pip install mast-aladin --upgrade


For details on installing and using mast-aladin, see the
`mast-aladin Installation <https://mast-aladin.readthedocs.io/en/latest/installation.html>`_.


Once installed, ``mast-aladin`` can be used in a jupyter lab notebook to visualize astronomical data interactively.
See the `mast-aladin docs <https://mast-aladin.readthedocs.io/en/latest/index.html>`_ for more details on installation and usage.

Running 
^^^^^^^

To get started with ``mast-aladin``, import it in your jupyter lab notebook as follows:

.. code-block:: python

   from mast_aladin import MastAladin

   mast_aladin = MastAladin()
   mast_aladin.show()

.. image:: https://github.com/spacetelescope/widget-docs/blob/main/mast-aladin/getting_started/cell0.jpg?raw=true
    :width: 70%
    :align: center

|

By default, ``mast_aladin.show()`` displays the widget in a `sidecar <https://github.com/jupyter-widgets/jupyterlab-sidecar>`_. You can control the location of the sidecar using the ``loc`` parameter of the ``show`` method, for example: ``mast_aladin.show(loc="sidecar:split-right")``.

``mast-aladin`` also provides a directory of `sample notebooks <https://github.com/spacetelescope/mast-aladin/tree/main/notebooks>`_ for reference and experimentation.

Help
----

If you encounter any unreported bugs or issues, please `open a GitHub issue <https://github.com/spacetelescope/mast-aladin/issues/new/choose>`_.

License & Attribution
---------------------

This project is Copyright (c) Space Telescope Science Institute and licensed under
the terms of the BSD 3-Clause license. See the
`licenses <https://github.com/spacetelescope/mast-aladin/tree/main/licenses>`_
folder for more information on works the mast-aladin package is derived from or distributes.
