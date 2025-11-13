import ipywidgets as widgets
from IPython.display import display

from mast_aladin.adapters import ImvizSyncAdapter, AladinSyncAdapter, SyncManager


class ViewerSyncUI():
    def __init__(self):

        self.mast_aladin = AladinSyncAdapter()
        self.imviz = ImvizSyncAdapter()
        self.sync_manager = SyncManager()
        self.aspects = self.sync_manager.aspects

        self.viewer_buttons = widgets.ToggleButtons(
            options=['None', 'Imviz', 'Mast Aladin'],
            disabled=False,
            button_style='',
            tooltips=['No Syncing', 'Sync to Imviz', 'Sync to Mast Aladin'],
            style=widgets.ToggleButtonsStyle(button_width="25%")
        )

        self.viewer_buttons.observe(self._handle_viewer_sync, names="value")

        common_togglebutton_args = {
            "value": True,
            "disabled": False,
            "button_style": "",
            "layout": widgets.Layout(width="25%")
        }

        for aspect in self.aspects:
            _attr = f"{aspect}_button"
            _togglebutton_args = {"description": aspect, "tooltip": f"Sync {aspect}"}
            setattr(
                self,
                _attr,
                widgets.ToggleButton(**common_togglebutton_args, **_togglebutton_args)
            )
            getattr(self, _attr).observe(self._handle_viewer_sync, names="value")

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
        return [
            aspect for aspect in self.aspects
            if getattr(
                getattr(self, f"{aspect}_button", None),
                "value",
                False
            )
        ]

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

    def display(self):
        self.imviz.layout = widgets.Layout(width="70%", height="100px")
        self.mast_aladin.layout = widgets.Layout(width="70%", height="100px")

        self.imviz.show()
        display(self.viewer_buttons)
        display(widgets.HBox([self.center_button, self.fov_button, self.rotation_button]))
        self.mast_aladin.show()
