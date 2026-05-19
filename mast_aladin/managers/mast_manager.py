from .app_manager import AppManager


class MastManager():
    """
    Coordinates interactions and overall workflow between components of the MAST Aladin ecosystem
    Ensures seamless integration and communication between applications, plugins, and sidecars.
    """
    def __init__(self):
        self._app_manager = AppManager(self)
        # todo: add the other managers here
        # - sidecar manager: responsible for managing sidecar windows.abs
        # - plugin manager: responsible for managing plugins (viewer sync, viewport sync, etc.)

    @property
    def AppManager(self):
        return self._app_manager

    @property
    def apps(self):
        return self._app_manager.apps

    def register_app(self, app, id):
        """
        This is a passthrough method that allows users to register an app to the AppManager
        directly from the MastManager.This is the recommended way to register apps, as it
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
