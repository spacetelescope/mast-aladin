from .app_manager import AppManager
from .plugin_manager import PluginManager
from sidecar import Sidecar
from jdaviz.configs.deconfigged import App as JdavizApp
from IPython.display import display


class MastManager():
    """
    Coordinates interactions and overall workflow between components of the MAST Aladin ecosystem
    Ensures seamless integration and communication between applications, plugins, and sidecars.
    """
    def __init__(self):
        self._app_manager = AppManager(self)
        self._plugin_manager = PluginManager(self)
        # todo: add the other managers here
        # - sidecar manager: responsible for managing sidecar windows.abs

    def close(self):
        self._app_manager.close()
        self._plugin_manager.close()

    @property
    def AppManager(self):
        return self._app_manager

    @property
    def apps(self):
        return self._app_manager.apps

    @property
    def PluginManager(self):
        return self._plugin_manager

    @property
    def plugins(self):
        return self._plugin_manager.plugins

    def register_app(self, app, id):
        """
        This is a passthrough method that allows users to register an app to the AppManager
        directly from the MastManager. This is the recommended way to register apps, as it
        allows the MastManager to keep track of all registered applications and facilitate
        communication between them as needed.

        Parameters
        ----------
        app : object
            The application instance to be registered.

        id : str
            A unique identifier for the application.
        """
        self._app_manager.register_app(app, id)
        # communicate this change to other managers as needed (e.g. plugin manager, sidecar manager)

    def display_plugin(self, plugin_id):
        self._plugin_manager.display_plugin(plugin_id)

    def display_plugins(self):
        self._plugin_manager.display()

    def display_apps(self):
        self._app_manager.check_for_new_instances(None)
        prev_ref = None
        prev_anchor = None
        for name, app in self._app_manager.apps.items():
            if prev_anchor is None:
                prev_anchor = 'split-right'
            elif prev_anchor == 'split-right':
                prev_anchor = 'split-bottom'
            else:
                prev_anchor = 'split-right'

            sc = Sidecar(title=name, anchor=prev_anchor, ref=prev_ref)
            with sc:
                if isinstance(app, JdavizApp):
                    app.show()
                else:
                    display(app)
            prev_ref = sc
