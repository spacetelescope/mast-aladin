import ipyvuetify as v
from pathlib import Path
from IPython.display import display
from mast_aladin.aida import AIDA_aspects
from .viewer_sync_adapters import get_adapter
from mast_aladin.components import AspectSelector, DestinationSelector, SourceSelector, Switch


VIEWER_SYNC_CSS = Path(__file__).with_name("viewer_sync.css").read_text()


class ViewerSync():
    def __init__(self, app_manager):
        self.app_manager = app_manager

        # register plugin to update adapters as registered apps change
        self._adapters = {}
        self.app_manager.observe(self._on_apps_changed, names=["_apps_changed"])

        self.sync_manager = ViewerSyncManager()
        self.aspects = self.sync_manager.aspects
        self._syncing = False

        # create UI components
        self.source_dropdown = SourceSelector(
            columns=list(self._adapters.keys()),
        )
        self.destination_dropdown = DestinationSelector(
            columns=list(self._adapters.keys()),
        )
        self.aspects_selector = AspectSelector(
            options=["center", "fov", "rotation", "projection"],
            descriptions={
                "center": "Synchronize the Center of the viewers.",
                "fov": "Synchronize the Field of View (FOV) of the viewers.",
                "rotation": "Synchronize the WCS rotation applied to the viewers.",
                "projection": "Synchronize the WCS projection applied to the viewers.",
            },
        )
        self.sync_switch = Switch()

        # set up observers for UI components
        self.source_dropdown.observe(self._source_on_change, names="selected_column")
        self.destination_dropdown.observe(self._destination_on_change, names="selected_columns")
        self.aspects_selector.observe(self._aspects_on_change, names="selected")
        self.sync_switch.observe(self._sync_switch_on_change, names="value")

    def close(self):
        self.app_manager.unobserve(self._on_apps_changed, names=["_apps_changed"])
        self._stop_sync()

    @property
    def ui(self):
        styles = v.Html(tag="style", children=[VIEWER_SYNC_CSS])
        header = v.Html(tag="h3", children=["Viewer Sync"])
        description = v.Html(tag="p", children=[
            """
            To sync: choose a source widget, select the destination widget(s) that
            should follow it, and specify which viewport properties to keep
            synchronized.
            """
        ])

        return v.Container(
            children=[
                styles,
                header,
                description,
                self.source_dropdown,
                self.destination_dropdown,
                self.aspects_selector,
                self.sync_switch,
            ],
            class_="viewer-sync-plugin flex-column",
            style_="display: flex; align-items: flex-start; width: min-content; max-width: 100%; padding: 0;",  # noqa: E501
        )

    def _source_on_change(self, change):
        # if the source changes while syncing, we want to stop syncing.
        if self._syncing:
            self._stop_sync()
        self._refresh_disabled_adapters()
        self._update_sync_switch_status()

    def _destination_on_change(self, change):
        # if the destination changes while syncing, we want to stop syncing.
        if self._syncing:
            self._stop_sync()
        self._update_sync_switch_status()

    def _update_sync_switch_status(self):
        # Enable the sync switch only if a source and at least one destination are selected
        if self.source_dropdown.selected_column and any(self.destination_dropdown.selected_columns):
            self.sync_switch.disabled = False
        else:
            self.sync_switch.disabled = True

    def _sync_switch_on_change(self, change):
        self._update_sync_switch_status()

        if change["new"] == "Stop Sync" and not self._syncing:
            self._start_sync()
        elif change["new"] == "Sync" and self._syncing:
            self._stop_sync(update_switch=False)

    def _aspects_on_change(self, change):
        if self._syncing:
            self._start_sync()

    def _start_sync(self, btn=None):
        source = self.source_dropdown.selected_column
        destinations = self.destination_dropdown.selected_columns

        source_adapter = self._adapters[source]
        dest_adapters = [self._adapters[d] for d in destinations]

        aspects = self._get_active_aspects()
        self.sync_manager.start_real_time_sync(
            source=source_adapter,
            destinations=dest_adapters,
            aspects=aspects
        )
        self._syncing = True

    def _stop_sync(self, update_switch=True):
        self.sync_manager.stop_real_time_sync()
        self._syncing = False
        if update_switch:
            self.sync_switch.value = "Sync"

    def _get_active_aspects(self):
        return self.aspects_selector.selected

    def _on_apps_changed(self, change):
        active_adapters = {
            self.source_dropdown.selected_column: self.sync_manager.source,
            **dict(zip(
                self.destination_dropdown.selected_columns,
                self.sync_manager.destinations,
            )),
        } if self._syncing else {}
        self._refresh_adapters()

        active_adapter_changed = any(
            self._adapters.get(name) is not adapter
            for name, adapter in active_adapters.items()
        )
        if active_adapter_changed:
            self._stop_sync(update_switch=False)

        self._refresh_dropdowns()

        if active_adapter_changed:
            source = self.source_dropdown.selected_column
            destinations = self.destination_dropdown.selected_columns
            if (
                source in self._adapters
                and destinations
                and all(name in self._adapters for name in destinations)
            ):
                self._start_sync()
            else:
                self.sync_switch.value = "Sync"

    def _refresh_dropdowns(self):
        new_options = list(self._adapters.keys())
        self.source_dropdown.columns = new_options
        self.destination_dropdown.columns = new_options
        self._refresh_disabled_adapters()

    def _refresh_disabled_adapters(self):
        disabled = [
            name for name, adapter in self._adapters.items()
            if not adapter.ready
        ]
        self.source_dropdown.set_disabled_columns(*disabled)

        source = self.source_dropdown.selected_column
        if source:
            disabled.append(source)
        self.destination_dropdown.set_disabled_columns(*disabled)

    def _refresh_adapters(self):
        # remove adapters for apps that are no longer present
        new_adapters = {}

        for name, app in self.app_manager.apps.items():
            existing_adapter = self._adapters.get(name)
            existing_app = getattr(
                existing_adapter,
                "app",
                getattr(existing_adapter, "viewer", None),
            )
            if existing_app is app:
                new_adapters[name] = existing_adapter
                continue

            adapter = get_adapter(app)
            if adapter is not None:
                new_adapters[name] = adapter(app)

        self._adapters = new_adapters

    def display(self):
        display(self.ui)


class ViewerSyncManager():
    def __init__(self):
        self.source = None
        self.destinations = []
        self.aspects = (
            AIDA_aspects.CENTER,
            AIDA_aspects.FOV,
            AIDA_aspects.ROTATION,
            AIDA_aspects.PROJECTION
        )

    def _callback(self, caller):
        for destination in self.destinations:
            destination.sync_to(self.source, self.aspects)

    def start_real_time_sync(self, source, destinations, aspects):
        # ensure we stop any previously configured real time sync
        self.stop_real_time_sync()

        self.source = source
        self.destinations = destinations
        self.aspects = aspects

        # add a callback to the source to update the destination when the view changes
        self.source.add_callback(self._callback)

        # call the sync method once manually to align the views
        for destination in self.destinations:
            destination.sync_to(self.source, self.aspects)

    def stop_real_time_sync(self):
        prev_source = self.source
        self.source = None
        self.destinations = []
        self.aspects = []

        if prev_source:
            prev_source.remove_callback(self._callback)
