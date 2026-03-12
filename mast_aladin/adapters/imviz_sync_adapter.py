from .viewer_sync_adapter import ViewerSyncAdapter
import warnings
import jdaviz

class ImvizSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        if viewer:
            self.app = viewer
        else:
            self.app = jdaviz.gca()

        # Get the first available viewer
        if self.app.viewers:
            first_viewer_key = list(self.app.viewers.keys())[0]
            self.viewer = self.app.viewers[first_viewer_key]
        else:
            raise ValueError(
                "No viewers available in jdaviz app. You must "
                "load data or create a viewer before using ImvizSyncAdapter."
            )

        self.aid = self.viewer._obj.glue_viewer.aid
        self.state = self.viewer._obj.glue_viewer.state

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
        try:
            orientation = self.app.plugins.get('Orientation')
            if orientation:
                orientation.align_by = 'WCS'
                orientation.set_north_up_east_left()
        except Exception as e:
            warnings.warn(f"Could not configure orientation: {e}")
