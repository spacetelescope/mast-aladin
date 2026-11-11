from .viewer_sync_adapter import ViewerSyncAdapter
import warnings
from mast_aladin.utils.optional_deps import import_jdaviz


class JdavizSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):

        jdaviz = import_jdaviz()

        if viewer:
            self.app = viewer
        elif jdaviz is not None:
            self.app = jdaviz.gca()

        # Get the first available image viewer
        image_viewers = self.app._app.get_viewers_of_cls('ImvizImageView')
        if image_viewers:
            glue_viewer = image_viewers[0]
        else:
            raise ValueError(
                "No compatible viewers available in jdaviz. You must "
                "load data with a world coordinate system before using ImvizSyncAdapter."
            )

        self.viewer = self.app.viewers[glue_viewer._ref_or_id]

        # TODO (2026-07-22): the jdaviz glue viewer attribute `aid`
        # will be removed in a PR coming soon, the line below will
        # need to be updated.
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
