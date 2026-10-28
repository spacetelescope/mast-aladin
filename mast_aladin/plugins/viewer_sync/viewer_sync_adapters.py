from IPython.display import display
from mast_aladin.app import gca, MastAladin
import warnings
import jdaviz
from jdaviz.configs.deconfigged import App as JdavizApp

from abc import ABC, abstractmethod
from mast_aladin.aida import AIDA_aspects


def get_adapter(app):
    if isinstance(app, MastAladin):
        return MastAladinSyncAdapter

    if isinstance(app, JdavizApp):
        return JdavizSyncAdapter

    return None


class ViewerSyncAdapter(ABC):
    @property
    def ready(self):
        return True

    def sync_to(self, sync_viewer, aspects):
        source_viewport = sync_viewer.aid.get_viewport(sky_or_pixel="sky")

        new_viewport = self.aid.get_viewport(sky_or_pixel="sky").copy()
        for aspect in set(aspects) & {*AIDA_aspects}:
            new_viewport[aspect] = source_viewport[aspect]

        self.aid.set_viewport(**new_viewport)

    @abstractmethod
    def add_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def remove_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def show(self):
        raise NotImplementedError


class MastAladinSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        self.viewer = viewer if viewer else gca()
        self.aid = self.viewer

    def add_callback(self, func):
        self.viewer.observe(func, names=["_target", "_fov", "_rotation", "_projection"])

    def remove_callback(self, func):
        self.viewer.unobserve(func, names=["_target", "_fov", "_rotation", "_projection"])

    def show(self):
        display(self.viewer)


class JdavizSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        self.app = viewer if viewer else jdaviz.gca()
        self._orientation_configured = self._configure_orientation()

    def _configure_orientation(self, warn=True):
        """Configure WCS alignment and orientation in jdaviz."""
        orientation = self.app.plugins.get('Orientation')
        if orientation is None:
            return False

        try:
            orientation.align_by = 'WCS'
        except Exception as e:
            if warn:
                warnings.warn(f"Could not configure WCS alignment: {e}")
            return False

        try:
            orientation.set_north_up_east_left()
        except Exception as e:
            if warn:
                warnings.warn(f"Could not configure orientation: {e}")
            return False

        return True

    @property
    def viewer(self):
        return self.app.viewers.get('Image')

    @property
    def state(self):
        if self.viewer is None:
            return None
        return self.viewer._obj.glue_viewer.state

    @property
    def aid(self):
        return self.viewer

    @property
    def ready(self):
        if self.viewer is None:
            return False

        if not self._orientation_configured:
            self._orientation_configured = self._configure_orientation(warn=False)

        return self._orientation_configured

    def sync_to(self, sync_viewer, aspects):
        if not self.ready:
            return

        # Remove "projection" from the list of aspects to sync, as it is not supported in jdaviz.
        if "projection" in aspects:
            aspects.remove("projection")

        super().sync_to(sync_viewer, aspects)

    def add_callback(self, func):
        if not self.ready:
            return

        for name in ['x_min', 'reference_data']:
            try:
                self.state.add_callback(name, func)
            except Exception as e:
                warnings.warn(f"Failed to add callback {name}: {e}")

    def remove_callback(self, func):
        if self.state is None:
            return

        for name in ['x_min', 'reference_data']:
            try:
                self.state.remove_callback(name, func)
            except Exception as e:
                warnings.warn(f"Failed to remove callback {name}: {e}")

    def show(self):
        self.app.show()
