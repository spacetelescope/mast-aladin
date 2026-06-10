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
            options=['None', 'Jdaviz', 'Mast Aladin'],
            disabled=False,
            button_style='',
            tooltips=['No Syncing', 'Sync to Jdaviz', 'Sync to Mast Aladin'],
            style=widgets.ToggleButtonsStyle(button_width="24%")
        )

        self.viewer_buttons.observe(self._handle_viewer_sync, names="value")

        common_togglebutton_args = {
            "value": True,
            "disabled": False,
            "button_style": "",
            "layout": widgets.Layout(width="24%")
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
            case "Jdaviz":
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

        # Jdaviz does not currently support setting projection, so we disable the projection
        # syncing option when Jdaviz is the destintation
        if dest == self.imviz:
            self.projection_button.value = False
            self.projection_button.disabled = True
        else:
            self.projection_button.value = True
            self.projection_button.disabled = False

        aspects = self._get_active_aspects()
        self.sync_manager.start_real_time_sync(
            source=source,
            destination=dest,
            aspects=aspects
        )

    def display(self):
        header_style = (
            "font-size: 12px; "
            "font-weight: 600; "
        )

        viewer_target_label = widgets.HTML(
            f"<div style='{header_style}'>Source Widget</div>"
        )

        sync_properties_label = widgets.HTML(
            f"<div style='{header_style}'>Properties</div>"
        )

        properties_row_1 = widgets.HBox([
            self.center_button,
            self.fov_button
        ], layout=widgets.Layout(width="100%", gap="12px", margin="0"))

        properties_row_2 = widgets.HBox([
            self.rotation_button,
            self.projection_button
        ], layout=widgets.Layout(width="100%", gap="12px", margin="0"))

        contents = [
            viewer_target_label,
            self.viewer_buttons,
            sync_properties_label,
            properties_row_1,
            properties_row_2,
        ]
        container = widgets.VBox(
            contents,
            layout=widgets.Layout(
                width="100%",
                padding="20px",
                border="1px solid"
            )
        )

        display(container)
