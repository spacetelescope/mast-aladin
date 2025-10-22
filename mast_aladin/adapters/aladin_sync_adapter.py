from IPython.display import display
from mast_aladin.app import gca

from .viewer_sync_adapter import ViewerSyncAdapter


class AladinSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        self.viewer = viewer if viewer else gca()
        self.aid = self.viewer.aid

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
        self.viewer.observe(func, names=["target", "fov", "rotation"])

    def remove_callback(self, func):
        for name in ["target", "fov", "rotation"]:
            try:
                self.viewer.unobserve(func, names=[name])
            except (ValueError, KeyError):
                pass

    def show(self):
        display(self.viewer)
