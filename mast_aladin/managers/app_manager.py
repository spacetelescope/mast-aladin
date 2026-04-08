from traitlets import HasTraits, Dict, observe, Int


class AppManager(HasTraits):
    """
    This class is responsible for managing the state of all applications within the
    MAST Aladin ecosystem. Any application registered to the AppManager will be tracked
    and can be accessed by other components (e.g. plugins, sidecars) to facilitate 
    communication and synchronization between different parts of the system.
    """

    _apps = Dict(default_value={}).tag(sync=True)

    def __init__(self, mast_manager):
        self._mast_manager = mast_manager

    @property
    def apps(self):
        return self._apps

    def get_app(self, idx):
        return self._apps.get(idx, None)

    def register_app(self, app, idx):
        """
        Registers an application to the AppManager with a unique identifier.
        If the identifier is already in use, a ValueError is raised.

        Parameters
        ----------
        app : object
            The application instance to be registered.

        idx : str
            A unique identifier for the application.
        """
        if idx in self._apps:
            raise ValueError(   
                f"id: {idx} already registered to an application. Please use a different, unique, identifier"  # noqa: E501
            )
        self._apps[idx] = app
