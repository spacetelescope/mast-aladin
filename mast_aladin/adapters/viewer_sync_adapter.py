from abc import ABC, abstractmethod
from mast_aladin.aida import AIDA_aspects


class ViewerSyncAdapter(ABC):
    def sync_to(self, sync_viewer, aspects):
        source_viewport = sync_viewer.aid.get_viewport(sky_or_pixel="sky")

        new_viewport = self.aid.get_viewport(sky_or_pixel="sky").copy()
        for aspect in set(aspects) & {AIDA_aspects.CENTER, AIDA_aspects.FOV, AIDA_aspects.ROTATION}:
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
