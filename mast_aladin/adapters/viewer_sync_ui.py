import ipywidgets as widgets
from IPython.display import display

from mast_aladin.adapters import ImvizSyncAdapter, AladinSyncAdapter, SyncManager


class ViewerSyncUI():
    def __init__(self):

        self.mast_aladin = AladinSyncAdapter()
        self.imviz = ImvizSyncAdapter()
        self.sync_manager = SyncManager()

        self.viewer_buttons = widgets.ToggleButtons(
            options=['None', 'Imviz', 'Mast Aladin'],
            disabled=False,
            button_style='',
            tooltips=['No Syncing', 'Sync to Imviz', 'Sync to Mast Aladin'],
            style=widgets.ToggleButtonsStyle(button_width="25%")
        )

        self.viewer_buttons.observe(self._handle_viewer_sync, names="value")

        self.center_button = widgets.ToggleButton(
            value=True,
            description='center',
            disabled=False,
            button_style='',
            tooltip='Sync center',
            layout=widgets.Layout(width="25%")
        )

        self.fov_button = widgets.ToggleButton(
            value=True,
            description='fov',
            disabled=False,
            button_style='',
            tooltip='Sync fov',
            layout=widgets.Layout(width="25%")
        )

        self.rotation_button = widgets.ToggleButton(
            value=True,
            description='rotation',
            disabled=False,
            button_style='',
            tooltip='Sync rotation',
            layout=widgets.Layout(width="25%")
        )

        self.center_button.observe(self._handle_aspect_change, names="value")
        self.fov_button.observe(self._handle_aspect_change, names="value")
        self.rotation_button.observe(self._handle_aspect_change, names="value")

    def _current_sync_direction(self):
        """Return (source, destination) tuple or (None, None)."""
        match self.viewer_buttons.value:
            case "Imviz":
                return self.imviz, self.mast_aladin
            case "Mast Aladin":
                return self.mast_aladin, self.imviz
            case _:
                return None, None

    def _get_active_aspects(self):
        active = []
        if self.center_button.value:
            active.append("center")
        if self.fov_button.value:
            active.append("fov")
        if self.rotation_button.value:
            active.append("rotation")
        return active

    def _handle_viewer_sync(self, change):
        if change.get("name") != "value" or change["new"] == change["old"]:
            return

        source, dest = self._current_sync_direction()
        if not source or not dest:
            self.sync_manager.stop_real_time_sync()
            return

        aspects = self._get_active_aspects()
        self.sync_manager.start_real_time_sync(
            source=source,
            destination=dest,
            aspects=aspects
        )

    def _handle_aspect_change(self, change):
        if change.get("name") != "value" or change["new"] == change["old"]:
            return

        source, dest = self._current_sync_direction()
        if not source or not dest:
            self.sync_manager.stop_real_time_sync()
            return

        aspects = self._get_active_aspects()
        self.sync_manager.start_real_time_sync(
            source=source,
            destination=dest,
            aspects=aspects
        )

    def display(self):
        self.imviz.layout = widgets.Layout(width="70%", height="100px")
        self.mast_aladin.layout = widgets.Layout(width="70%", height="100px")

        self.imviz.show()
        display(self.viewer_buttons)
        display(widgets.HBox([self.center_button, self.fov_button, self.rotation_button]))
        self.mast_aladin.show()
