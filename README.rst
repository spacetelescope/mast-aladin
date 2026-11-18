.. |stsci-logo| image:: docs/assets/mast-aladin-logo.svg
    :alt: STScI logo
    :height: 200px

|stsci-logo|

.. image:: https://github.com/spacetelescope/mast-aladin/actions/workflows/ci_workflows.yml/badge.svg
    :target: https://github.com/spacetelescope/mast-aladin/actions/workflows/ci_workflows.yml
    :alt: GitHub Actions CI Status

.. image:: https://codecov.io/gh/spacetelescope/mast-aladin/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/spacetelescope/mast-aladin

.. image:: https://readthedocs.org/projects/mast-aladin/badge/?version=latest
    :target: https://mast-aladin.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status



``mast-aladin`` adds convenience methods for visualizing and interacting with query results from MAST on the Aladin sky atlas, including queries for observations and sources in catalogs. ``mast-aladin`` is Python package maintained by the Space Telescope Science Institute that extends `ipyaladin <https://github.com/cds-astro/ipyaladin>`_, a package maintained by CDS (Centre de Données astronomiques de Strasbourg). ``ipyaladin`` is a Jupyter widget wrapper for `aladin-lite <https://github.com/cds-astro/aladin-lite>`_, also maintained by CDS.

Key Features
------------

- Runs in Jupyter notebooks locally or on the `Roman Research Nexus <https://roman.science.stsci.edu/>`_.
- Provides interactive access through the Aladin Lite interface and a Python API, with all-sky imaging from surveys including SDSS, Pan-STARRS, WISE, GALEX, and more.
- Visualizes and interacts with MAST observation and catalog query results. Includes plotting observation footprints and source catalog plotting tools, and works with `mast-table <https://github.com/spacetelescope/mast-table>`_ results.
- Integrates with `jdaviz <https://jdaviz.readthedocs.io/en/stable/>`_ through the AIDA (Astronomical Interactive Data Analysis) framework.

Installing
----------

Installing ``mast-aladin`` in a new virtual or conda environment will help you to avoid 
version conflicts with other packages you may have installed, for example:

.. code-block:: bash

   conda create -n mast-aladin-env python=3.12
   conda activate mast-aladin-env

You can install the latest stable release version of ``mast-aladin`` using pip:

.. code-block:: bash

   pip install mast-aladin --upgrade

Or, you can install the latest development version of ``mast-aladin`` using pip:

.. code-block:: bash

   pip install git+https://github.com/spacetelescope/mast-aladin --upgrade

For details on installing and using mast-aladin, see the
`mast-aladin Installation <https://mast-aladin.readthedocs.io/en/latest/installation.html>`_.

Quick Start
-----------

Once installed, ``mast-aladin`` can be used in a jupyter lab notebook to visualize astronomical data interactively.
See the `mast-aladin docs <https://mast-aladin.readthedocs.io/en/latest/index.html>`_ for more details on installation and usage.


To get started with ``mast-aladin``, import it in your jupyter lab notebook as follows:

.. code-block:: python

   from mast_aladin import MastAladin

   mast_aladin = MastAladin()
   mast_aladin.show()

.. image:: https://github.com/spacetelescope/widget-docs/blob/main/mast-aladin/getting_started/cell0.jpg?raw=true
    :width: 70%
    :align: center

|

``mast-aladin`` also provides a directory of `sample notebooks <https://github.com/spacetelescope/mast-aladin/tree/main/notebooks>`_ for reference and experimentation.

Help
----------

If you encounter any unreported bugs or issues, please `open a GitHub issue <https://github.com/spacetelescope/mast-aladin/issues/new/choose>`_.

License & Attribution
---------------------

This project is Copyright (c) Space Telescope Science Institute and licensed under
the terms of the BSD 3-Clause license. See the
`licenses <https://github.com/spacetelescope/mast-aladin/tree/main/licenses>`_
folder for more information on works the mast-aladin package is derived from or distributes.


Contributing
------------

We love contributions! ``mast-aladin`` is open source, built on open source, and we'd love to have you hang out in our community.

**Imposter syndrome disclaimer:** We want your help. No, really.

There may be a little voice inside your head that is telling you that you're not ready to be an open source contributor; that your skills aren't nearly good enough to contribute. What could you possibly offer a project like this one?

We assure you - the little voice in your head is wrong. If you can write code at all, you can contribute code to open source. Contributing to open source projects is a fantastic way to advance one's coding skills. Writing perfect code isn't the measure of a good developer (that would disqualify all of us!); it's trying to create something, making mistakes, and learning from those mistakes. That's how we all improve, and we are happy to help others learn.

Being an open source contributor doesn't just mean writing code, either. You can help out by writing documentation, tests, or even giving feedback about the project (and yes - that includes giving feedback about the contribution process). Some of these contributions may be the most valuable to the project as a whole, because you're coming to the project with fresh eyes, so you can see the errors and assumptions that seasoned contributors have glossed over.

Note: This disclaimer was originally written by Adrienne Lowe for a PyCon talk, and was adapted by ``mast-aladin`` based on its use in the README file for the MetPy project.