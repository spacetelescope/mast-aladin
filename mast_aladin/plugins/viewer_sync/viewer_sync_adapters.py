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

        # Get the first available image viewer
        image_viewers = self.app._app.get_viewers_of_cls('ImvizImageView')
        if image_viewers:
            glue_viewer = image_viewers[0]
        else:
            raise ValueError(
                "No compatible viewers available in jdaviz. You must "
                "load data with a world coordinate system before using JdavizSyncAdapter."
            )

        self.viewer = self.app.viewers[glue_viewer._ref_or_id]
        self.aid = glue_viewer.aid
        self.state = glue_viewer.state

        self._configure_orientation()

    def _configure_orientation(self):
        """Configure WCS alignment and orientation in jdaviz."""
        orientation = self.app.plugins.get('Orientation')
        if orientation is None:
            return

        try:
            orientation.align_by = 'WCS'
            orientation.set_north_up_east_left()
        except Exception as e:
            warnings.warn(f"Could not configure orientation: {e}")

    def sync_to(self, sync_viewer, aspects):
        # Remove "projection" from the list of aspects to sync, as it is not supported in jdaviz.
        if "projection" in aspects:
            aspects.remove("projection")

        super().sync_to(sync_viewer, aspects)

    def add_callback(self, func):
        for name in ['x_min', 'reference_data']:
            try:
                self.state.add_callback(name, func)
            except Exception as e:
                warnings.warn(f"Failed to add callback {name}: {e}")

    def remove_callback(self, func):
        for name in ['x_min', 'reference_data']:
            try:
                self.state.remove_callback(name, func)
            except Exception as e:
                warnings.warn(f"Failed to remove callback {name}: {e}")

    def show(self):
        self.app.show()
