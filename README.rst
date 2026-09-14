.. image:: https://github.com/spacetelescope/mast-aladin/actions/workflows/ci_workflows.yml/badge.svg
    :target: https://github.com/spacetelescope/mast-aladin/actions/workflows/ci_workflows.yml
    :alt: GitHub Actions CI Status

.. image:: https://codecov.io/gh/spacetelescope/mast-aladin/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/spacetelescope/mast-aladin

.. image:: https://readthedocs.org/projects/mast-aladin/badge/?version=latest
    :target: https://mast-aladin.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

mast-aladin
===========

.. warning::

    mast-aladin is currently in heavy development and breaking changes may occur without warning.


While we experiment with Aladin Lite integration in MAST platforms, this repository can be used to contain:

- documentation
- support code for wrapping and integrating Aladin Lite
- demonstration notebooks

Once design plans become more concrete, we can decide whether to keep using this repository.

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

Help
----------

If you encounter any unreported bugs or issues, please `open a GitHub issue <https://github.com/spacetelescope/mast-aladin/issues/new/choose>`_

License & Attribution
---------------------

This project is Copyright (c) Space Telescope Science Institute and licensed under
the terms of the BSD 3-Clause license. See the
`licenses <https://github.com/spacetelescope/mast-aladin/tree/main/licenses>`_
folder for more information on works the mast-aladin package is derived from or distributes.
