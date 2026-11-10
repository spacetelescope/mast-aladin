import pytest
from traitlets import HasTraits, Int
import mast_aladin.plugins.viewer_sync.viewer_sync as viewer_sync_module
from mast_aladin.plugins.viewer_sync.viewer_sync import ViewerSync


class MockAdapter:
    def __init__(self, app):
        self.app = app
        self.callbacks = []

    @property
    def ready(self):
        return True

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        self.callbacks.remove(callback)

    def sync_to(self, source, aspects):
        pass


class StubAppManager(HasTraits):
    _apps_changed = Int()

    def __init__(self):
        super().__init__()
        self.apps = {}

    def refresh(self, apps):
        self.apps = apps
        self._apps_changed += 1


@pytest.fixture
def viewer_sync(monkeypatch):
    monkeypatch.setattr(viewer_sync_module, "get_adapter", lambda _app: MockAdapter)
    app_manager = StubAppManager()
    return ViewerSync(app_manager)


def start_sync(viewer_sync, apps):
    viewer_sync.app_manager.refresh(apps)
    viewer_sync.source_dropdown.selected_column = "source"
    viewer_sync.destination_dropdown.selected_columns = ["destination"]
    viewer_sync.sync_switch.value = "Stop Sync"


def test_refresh_adapters_replaces_adapter_for_rebound_name(viewer_sync):
    original_app = object()
    replacement_app = object()
    viewer_sync.app_manager.refresh({"viewer": original_app})
    original_adapter = viewer_sync._adapters["viewer"]

    viewer_sync.app_manager.refresh({"viewer": replacement_app})

    assert viewer_sync._adapters["viewer"] is not original_adapter
    assert viewer_sync._adapters["viewer"].app is replacement_app


@pytest.mark.parametrize("rebound_name", ["source", "destination"])
def test_app_refresh_restarts_sync_when_active_adapter_is_rebound(
    viewer_sync, rebound_name
):
    apps = {"source": object(), "destination": object()}
    start_sync(viewer_sync, apps)
    original_source_adapter = viewer_sync.sync_manager.source
    refreshed_apps = dict(apps)
    refreshed_apps[rebound_name] = object()

    viewer_sync.app_manager.refresh(refreshed_apps)

    assert viewer_sync._syncing
    assert viewer_sync.sync_switch.value == "Stop Sync"
    assert viewer_sync.sync_manager.source is viewer_sync._adapters["source"]
    assert viewer_sync.sync_manager.destinations == [viewer_sync._adapters["destination"]]
    if rebound_name == "source":
        assert viewer_sync.sync_manager.source is not original_source_adapter
        assert original_source_adapter.callbacks == []


def test_app_refresh_stays_stopped_when_active_destination_is_removed(
    viewer_sync,
):
    source_app = object()
    destination_app = object()
    start_sync(viewer_sync, {"source": source_app, "destination": destination_app})

    viewer_sync.app_manager.refresh({"source": source_app})

    assert not viewer_sync._syncing
    assert viewer_sync.sync_switch.value == "Sync"
    assert viewer_sync.sync_manager.source is None
    assert viewer_sync.destination_dropdown.selected_columns == []


def test_app_refresh_keeps_sync_when_inactive_adapter_is_rebound(viewer_sync):
    source_app = object()
    destination_app = object()
    original_inactive_app = object()
    replacement_inactive_app = object()
    apps = {
        "source": source_app,
        "destination": destination_app,
        "inactive": original_inactive_app,
    }
    start_sync(viewer_sync, apps)
    original_source_adapter = viewer_sync.sync_manager.source

    viewer_sync.app_manager.refresh({
        **apps,
        "inactive": replacement_inactive_app,
    })

    assert viewer_sync._syncing
    assert viewer_sync.sync_manager.source is original_source_adapter
    assert len(original_source_adapter.callbacks) == 1
