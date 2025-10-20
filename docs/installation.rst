User Installation
-----------------

.. note::

    The `mast-aladin` package is actively maintained, and improvements are made regularly.
    To ensure you have the latest features and bug fixes, we recommend updating to the most 
    recent version. The development version often includes the latest changes ahead of full releases.


Set Up Your Local Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To use mast-aladin, you need `Python 3.11` or later. Below is an example using `Python 3.11`, but you can 
replace 3.11 with any supported version (e.g., 3.12).

1. **Create a new Conda environment:**

.. code-block:: bash

    conda create -n mast-aladin-env python=3.11
    conda activate mast-aladin-env

2. **Install mast-aladin using pip:**

- To install the latest development version (includes the most recent updates and fixes):

.. code-block:: bash

    pip install git+https://github.com/spacetelescope/mast-aladin --upgrade

- To install the latest stable release

.. code-block:: bash

    pip install mast-aladin --upgrade

Setting Up a Local Development Copy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::

    To develop mast-aladin, you may need to run `brew install npm`
    before proceeding.

If you plan to contribute to mast-aladin or modify the code, 
follow these steps to set up a local development copy:

1. **Fork the mast-aladin repository**

- Go to the `mast-aladin GitHub repository <https://github.com/spacetelescope/mast-aladin>`_
- Click the Fork button.
- This creates a copy of the repository under your GitHub account.
  
2. **Clone your fork locally.**

- Replace your-username with your GitHub username:

.. code-block:: bash

    git clone git@github.com:username/mast-aladin.git
    cd mast-aladin

3. **Set up the upstream remote**

.. code-block:: bash

    git remote add upstream git@github.com:spacetelescope/mast-aladin.git
    git fetch upstream main
    git fetch upstream --tags

4. **Keep your fork updated**

- Before starting new work, update your local ``main`` branch with the 
  latest changes from the upstream repository:

.. code-block:: bash

    git checkout main
    git pull upstream main



