Plugins
=======

The ``mast-aladin`` package supports plugins that extend its functionality. Plugins provide interoperability between `~mast_aladin.app.MastAladin` and other visualization tools (e.g. `jdaviz <https://jdaviz.readthedocs.io/>`_). For more information on accessing the plugins API, see the :doc:`accessing_plugins_api` page.


.. toctree::
   :hidden:

   viewer_sync

Currently supported plugins
---------------------------
- :doc:`Viewer Sync <viewer_sync>` (``viewer_sync``) keeps selected viewport properties synchronized between `~mast_aladin.app.MastAladin` and ``jdaviz`` image viewers.