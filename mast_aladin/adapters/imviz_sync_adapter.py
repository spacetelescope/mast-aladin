from .viewer_sync_adapter import ViewerSyncAdapter


class ImvizSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        # todo: assert the type of the viewer is jdaviz/imviz
        from jdaviz.configs.imviz.helper import _current_app
        self.app = viewer if viewer else _current_app
        self.viewer = self.app.default_viewer
        self.aid = self.viewer._obj.aid

    def sync_to(self, sync_viewer):
        self.aid.set_viewport(**sync_viewer.aid.get_viewport())

    def add_callback(self, func):
        self.viewer._obj.state.add_callback('zoom_radius', func)

    def remove_callback(self, func):
        self.viewer._obj.state.remove_callback('zoom_radius', func)

    def show(self):
        self.app.show()
        self.app.link_data(align_by='wcs')
        self.app.plugins['Orientation'].set_north_up_east_left()
