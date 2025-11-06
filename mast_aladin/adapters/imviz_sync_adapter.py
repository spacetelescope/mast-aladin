from .viewer_sync_adapter import ViewerSyncAdapter
import warnings


class ImvizSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        from jdaviz.configs.imviz.helper import _current_app
        self.app = viewer if viewer else _current_app
        self.viewer = self.app.default_viewer
        self.aid = self.viewer._obj.glue_viewer.aid

    def sync_to(self, sync_viewer, aspects):
        source_viewport = sync_viewer.aid.get_viewport(sky_or_pixel="sky")

        new_viewport = self.aid.get_viewport(sky_or_pixel="sky").copy()
        if "center" in aspects:
            new_viewport["center"] = source_viewport["center"]
        if "fov" in aspects:
            new_viewport["fov"] = source_viewport["fov"]
        if "rotation" in aspects:
            new_viewport["rotation"] = source_viewport["rotation"]

        self.aid.set_viewport(**new_viewport)

    def add_callback(self, func):
        state = self.viewer._obj.glue_viewer.state
        for name in ['zoom_radius', 'x_min', 'x_max', 'y_min', 'y_max']:
            state.add_callback(name, func)

        try:
            self.app.plugins['Orientation'].rotation_angle.add_callback(func)
        except Exception as e:
            warnings.warn(f"Failed to add callback for rotation: {e}")

    def remove_callback(self, func):
        state = self.viewer._obj.glue_viewer.state
        for name in ['zoom_radius', 'x_min', 'x_max', 'y_min', 'y_max']:
            try:
                state.remove_callback(name, func)
            except Exception as e:
                warnings.warn(f"Failed to remove callback {name}: {e}")
        try:
            self.app.plugins['Orientation'].rotation_angle.remove_callback(func)
        except Exception as e:
            warnings.warn(f"Failed to remove callback for rotation: {e}")

    def show(self):
        self.app.show()
        self.app.link_data(align_by='wcs')
        self.app.plugins['Orientation'].set_north_up_east_left()
