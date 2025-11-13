from IPython.display import display
from mast_aladin.app import gca

from .viewer_sync_adapter import ViewerSyncAdapter
from mast_aladin.aida import AIDA_aspects


class AladinSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        self.viewer = viewer if viewer else gca()
        self.aid = self.viewer.aid

    def sync_to(self, sync_viewer, aspects):
        source_viewport = sync_viewer.aid.get_viewport(sky_or_pixel="sky")

        new_viewport = self.aid.get_viewport(sky_or_pixel="sky").copy()
        for aspect in set(aspects) & {AIDA_aspects.CENTER, AIDA_aspects.FOV, AIDA_aspects.ROTATION}:
            new_viewport[aspect] = source_viewport[aspect]

        self.aid.set_viewport(**new_viewport)

    def add_callback(self, func):
        self.viewer.observe(func, names=["_target", "_fov", "_rotation"])

    def remove_callback(self, func):
        self.viewer.unobserve(func, names=["_target", "_fov", "_rotation"])

    def show(self):
        display(self.viewer)
