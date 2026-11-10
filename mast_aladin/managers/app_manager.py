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
    _manual_apps = Dict(default_value={}).tag(sync=True)
    _auto_apps = Dict(default_value={}).tag(sync=True)
    _apps_changed = Int(default_value=0).tag(sync=True)

    def __init__(self, mast_manager):
        self._mast_manager = mast_manager
        self._ipython = get_ipython()
        if self._ipython is not None:
            self._ipython.events.register('post_run_cell', self.check_for_new_instances)

    def __del__(self):
        self.close()

    def close(self):
        if self._ipython is None:
            return
        self._ipython.events.unregister('post_run_cell', self.check_for_new_instances)
        self._ipython = None

    @property
    def apps(self):
        return {**self._auto_apps, **self._manual_apps}

    def get_app(self, id):
        return self.apps.get(id, None)

    def register_app(self, app, name):
        """
        Register an application.

        Manual registrations take precedence over automatically discovered
        applications with the same name. A ``ValueError`` is raised only when
        ``name`` is already used by another manually registered application.

        Parameters
        ----------
        app : object
            The application instance to be registered.

        name : str
            A unique identifier for the application.
        """
        if name in self._manual_apps:
            raise ValueError(
                f"name: {name} already registered to an application, unique names are required"  # noqa: E501
            )
        self._manual_apps[name] = app
        self._apps_changed += 1

    def check_for_new_instances(self, result):
        """
        Callback that runs automatically after every cell execution and is responsible
        for detecting new instances of supported viz apps in the global namespace
        and updating the internal registry accordingly.
        """
        if self._ipython is None:
            return

        globals_dict = self._ipython.user_ns

        # update self._apps with any new instances found in the global namespace
        new_apps = {
            name: obj
            for name, obj in globals_dict.items()
            if not name.startswith("_")
            and isinstance(obj, (MastAladin, JdavizApp))
        }

        # Update the internal registry with the new set of apps.
        if self._auto_apps != new_apps:
            self._auto_apps = new_apps

        # Notify consumers after every cell so they can refresh app readiness.
        self._apps_changed += 1
