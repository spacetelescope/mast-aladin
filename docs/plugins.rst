Plugins
=======

The ``mast-aladin`` package supports plugins that extend its functionality. Plugins provide interoperability between `~mast_aladin.app.MastAladin` and other visualization tools (e.g. `jdaviz <https://jdaviz.readthedocs.io/>`_).

.. toctree::
   :hidden:

   viewer_sync

Currently supported plugins
---------------------------

- :doc:`Viewer Sync <viewer_sync>` (``viewer_sync``) keeps selected viewport properties
  synchronized between `~mast_aladin.app.MastAladin` and ``jdaviz`` image
  viewers.


How to use
----------

The `~mast_aladin.managers.mast_manager.MastManager` class coordinates interactions between components of the MAST Aladin ecosystem. It uses `~mast_aladin.managers.app_manager.AppManager` to keep a registry of visualization applications assigned to variables in your jupyter lab notebook, and a `~mast_aladin.managers.plugin_manager.PluginManager`, which manages and displays the available plugins.

.. code-block:: python

    from mast_aladin import MastManager, MastAladin

    mast_manager = MastManager()

    mast_aladin_a = MastAladin()
    mast_aladin_b = MastAladin()

    mast_manager.display_plugins()

`~mast_aladin.managers.mast_manager.MastManager.display_plugins` displays all available plugins in a tabbed widget. A single plugin can be displayed on its own with `~mast_aladin.managers.mast_manager.MastManager.display_plugin`. 

.. code-block:: python

    mast_manager.display_plugin("viewer_sync")

Application registration
^^^^^^^^^^^^^^^^^^^^^^^^

Plugins operate on the applications registered with the `~mast_aladin.managers.app_manager.AppManager`. Applications are registered in two ways:

- **Automatic discovery**: after every notebook cell execution, the `~mast_aladin.managers.app_manager.AppManager` scans the notebook's global namespace for instances of `~mast_aladin.app.MastAladin` or ``jdaviz`` , and registers them under the variable names assigned to them in the notebook. In the example above, ``mast_aladin_a`` and ``mast_aladin_b`` are discovered automatically.
- **Manual registration**: applications can be registered explicitly with `~mast_aladin.managers.mast_manager.MastManager.register_app`, which takes the application instance and a unique identifier. Manual registrations take precedence over automatically discovered applications with the same name.

.. code-block:: python

    mast_manager.register_app(mast_aladin_a, "my_viewer")

All registered applications can be opened side-by-side in `sidecar <https://github.com/jupyter-widgets/jupyterlab-sidecar>`_ windows with `~mast_aladin.managers.mast_manager.MastManager.display_apps`.