from traitlets import HasTraits, Dict, Int
from IPython import get_ipython
from mast_aladin import MastAladin
from jdaviz.configs.deconfigged import App as JdavizApp

class AppManager(HasTraits):
    """
    Manages the state of applications within the MAST Aladin ecosystem. Tracks registered apps
    for access by other components (e.g. plugins, sidecars), and facilitates communication
    and synchronization between different parts of the system.
    """

    _apps = Dict(default_value={}).tag(sync=True)
    _apps_changed = Int(default_value=0).tag(sync=True)

    def __init__(self, mast_manager):
        self._mast_manager = mast_manager
        get_ipython().events.register('post_run_cell', self.check_for_new_instances)

    @property
    def apps(self):
        return self._apps

    def get_app(self, id):
        return self._apps.get(id, None)

    def register_app(self, app, name):
        """
        Registers an application to the AppManager with a unique identifier.
        If the identifier is already in use, a ValueError is raised.

        Parameters
        ----------
        app : object
            The application instance to be registered.

        name : str
            A unique identifier for the application.
        """
        if name in self._apps:
            raise ValueError(
                f"name: {name} already registered to an application. Please use a different, unique, identifier"  # noqa: E501
            )
        self._apps[name] = app
        self._apps_changed += 1

    def check_for_new_instances(self, result):
        """
        Callback that runs automatically after every cell execution and is responsible
        for detecting new instances of supported viz apps in the global namespace
        and updating the internal registry accordingly.
        
        """
        globals_dict = get_ipython().user_ns

        # update self._apps with any instances no longer present in the global namespace
        new_apps = {}
        for name, obj in self._apps.items():
            if id(obj) == id(globals_dict[name]):
                new_apps[name] = obj
        
        # update self._apps with any new instances found in the global namespace
        for name, obj in list(globals_dict.items()):
            # if the name starts with `_` then the user did not assign the instance to a variable and 
            # it displayed in a cell output. We are skipping the cell output instance.
            if name[0] == "_":
                continue

            # Check if the variable is an instance of supported viz apps and unregistered
            if isinstance(obj, (MastAladin, JdavizApp)) and name not in self._apps:
                new_apps[name] = obj
        
        # Update the internal registry with the new set of apps.
        if self._apps != new_apps:
            self._apps = new_apps

        # Notify consumers after every cell so they can refresh app readiness.
        self._apps_changed += 1
