mast-aladin
===========

``mast-aladin`` is an Aladin Lite widget for Jupyter notebooks for use with 
data products from the `Mikulski Archive for Space Telescopes (MAST) <https://mast.stsci.edu/>`_
from the `Space Telescope Science Institute <https://stsci.edu/>`_. 

The source code is available on `GitHub <https://github.com/spacetelescope/mast-aladin>`_.


Key Features
************

* **Runs on the** `Roman Research Nexus <https://roman.science.stsci.edu/hub/login?next=%2Fhub%2F>`_,
  or on your local machine in a Jupyter notebook
* **Browse all-sky imaging survey atlases** from surveys
  across the spectrum including SDSS, Pan-STARRS, WISE, GALEX, and more
* **Interactivity** via the familiar Aladin-Lite UI *and* via a Python API
* Plot **observation footprints** and **source catalogs** from MAST


Why mast-aladin?
^^^^^^^^^^^^^^^^

.. image:: https://github.com/spacetelescope/widget-docs/blob/main/mast-aladin/aladin-inheritance.png?raw=true
    :width: 80%
    :align: center

|

``mast-aladin`` is Python package maintained by the Space Telescope Science 
Institute that extends `ipyaladin <https://github.com/cds-astro/ipyaladin>`_, a package
maintained by CDS (Centre de Données astronomiques de Strasbourg). `ipyaladin` is
a Jupyter widget wrapper for `aladin-lite <https://github.com/cds-astro/aladin-lite>`_,
also maintained by CDS. ``mast-aladin`` adds convenience methods for visualizing
and interacting with query results from MAST on the Aladin sky atlas, including 
queries for observations and sources in catalogs.

``mast-aladin`` can run in any Jupyter notebook, including notebooks on the
`Roman Research Nexus <https://roman.science.stsci.edu/hub/login?next=%2Fhub%2F>`_.
``mast-aladin`` supports interaction with observation query results in
`mast-table <https://github.com/spacetelescope/mast-table>`_.



Contents
********

.. toctree::
   :maxdepth: 2

   installation
   getting_started
   performance_catalog
   api
