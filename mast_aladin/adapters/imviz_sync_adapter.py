from .viewer_sync_adapter import ViewerSyncAdapter
import warnings


class ImvizSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        from jdaviz.configs.imviz.helper import _current_app
        self.app = viewer if viewer else _current_app
        self.viewer = self.app.default_viewer
        self.aid = self.viewer._obj.glue_viewer.aid
        self.state = self.viewer._obj.glue_viewer.state

    def add_callback(self, func):
        try:
            self.state.add_callback('x_min', func)
        except Exception as e:
            warnings.warn(f"Failed to add callback for 'x_min': {e}")

        warnings.warn(
            "Rotation syncing from Imviz → Mast-Aladin is currently disabled. "
            "Changes in Imviz orientation will not propagate."
        )

    def remove_callback(self, func):
        try:
            self.state.remove_callback('x_min', func)
        except Exception as e:
            warnings.warn(f"Failed to remove callback for 'x_min': {e}")

    def show(self):
        self.app.show()
        self.app.link_data(align_by='wcs')
        self.app.plugins['Orientation'].set_north_up_east_left()
