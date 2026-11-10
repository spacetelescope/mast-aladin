import pytest
from unittest.mock import Mock, MagicMock
from IPython.core.interactiveshell import InteractiveShell
import mast_aladin.managers.app_manager as app_manager_module
from mast_aladin.managers.app_manager import AppManager


class TestAppManager:
    """Test suite for AppManager class."""

    @pytest.fixture
    def ipython_shell(self, monkeypatch):
        InteractiveShell.clear_instance()
        shell = InteractiveShell.instance()
        monkeypatch.setattr(app_manager_module, "get_ipython", lambda: shell)
        yield shell
        InteractiveShell.clear_instance()

    @pytest.fixture
    def supported_app_types(self, monkeypatch):
        class MockMastAladin:
            pass

        class MockJdavizApp:
            pass

        monkeypatch.setattr(app_manager_module, "MastAladin", MockMastAladin)
        monkeypatch.setattr(app_manager_module, "JdavizApp", MockJdavizApp)
        return MockMastAladin, MockJdavizApp

    @pytest.fixture
    def mock_mast_manager(self):
        """Create a mock MastManager instance."""
        return Mock()

    @pytest.fixture
    def app_manager(self, mock_mast_manager, ipython_shell):
        """Create an AppManager instance with a mock MastManager."""
        manager = AppManager(mock_mast_manager)
        yield manager
        manager.close()

    def test_initialization(self, app_manager, mock_mast_manager):
        """Test that AppManager initializes correctly."""
        assert app_manager._mast_manager is mock_mast_manager
        assert app_manager.apps == {}

    def test_register_app_single(self, app_manager):
        """Test registering a single application."""
        mock_app = Mock()
        app_manager.register_app(mock_app, "test_app")

        assert "test_app" in app_manager.apps
        assert app_manager.apps["test_app"] is mock_app

    def test_register_app_multiple(self, app_manager):
        mock_aladin = MagicMock(name="aladin")
        mock_imviz = MagicMock(name="imviz")
        mock_custom = MagicMock(name="custom_app")

        # Test with underscores
        app_manager.register_app(mock_aladin, "mast_aladin")
        assert "mast_aladin" in app_manager.apps

        # Test with hyphens
        app_manager.register_app(mock_imviz, "imviz-viewer")
        assert "imviz-viewer" in app_manager.apps

        # Test with just alphanumeric
        app_manager.register_app(mock_custom, "custom_app")
        assert "custom_app" in app_manager.apps

    def test_register_app_duplicate_id_raises_error(self, app_manager):
        """Test that registering an app with duplicate ID raises ValueError."""
        mock_app1 = Mock()
        mock_app2 = Mock()

        app_manager.register_app(mock_app1, "duplicate_id")

        with pytest.raises(ValueError) as exc_info:
            app_manager.register_app(mock_app2, "duplicate_id")

        assert "duplicate_id" in str(exc_info.value)
        assert "already registered" in str(exc_info.value)

    def test_get_app_existing(self, app_manager):
        """Test getting an existing app."""
        mock_app = Mock()
        app_manager.register_app(mock_app, "test_app")

        retrieved_app = app_manager.get_app("test_app")
        assert retrieved_app is mock_app

    def test_get_app_non_existent(self, app_manager):
        """Test getting a non-existent app returns None."""
        result = app_manager.get_app("non_existent")
        assert result is None

    def test_apps_property(self, app_manager):
        """Test apps property returns the apps dictionary."""
        mock_app = Mock()
        app_manager.register_app(mock_app, "test_app")

        apps_dict = app_manager.apps
        assert isinstance(apps_dict, dict)
        assert "test_app" in apps_dict
        assert apps_dict["test_app"] is mock_app

    def test_apps_property_empty(self, app_manager):
        """Test apps property when no apps are registered."""
        apps_dict = app_manager.apps
        assert isinstance(apps_dict, dict)
        assert len(apps_dict) == 0

    def test_auto_registers_supported_apps(
        self, app_manager, ipython_shell, supported_app_types
    ):
        mock_mast_aladin, mock_jdaviz_app = supported_app_types
        ipython_shell.push({
            "MockMastAladin": mock_mast_aladin,
            "MockJdavizApp": mock_jdaviz_app,
        })

        ipython_shell.run_cell(
            "aladin = MockMastAladin()\n"
            "jdaviz = MockJdavizApp()"
        )

        assert app_manager.apps == {
            "aladin": ipython_shell.user_ns["aladin"],
            "jdaviz": ipython_shell.user_ns["jdaviz"],
        }

    def test_auto_registration_ignores_private_and_unsupported_names(
        self, app_manager, ipython_shell, supported_app_types
    ):
        mock_mast_aladin, _ = supported_app_types
        ipython_shell.push({"MockMastAladin": mock_mast_aladin})

        ipython_shell.run_cell(
            "_cell_output = MockMastAladin()\n"
            "table = object()"
        )

        assert app_manager.apps == {}

    def test_auto_registration_removes_deleted_names(
        self, app_manager, ipython_shell, supported_app_types
    ):
        mock_mast_aladin, _ = supported_app_types
        ipython_shell.push({"MockMastAladin": mock_mast_aladin})
        ipython_shell.run_cell("viewer = MockMastAladin()")

        ipython_shell.run_cell("del viewer")

        assert "viewer" not in app_manager.apps

    def test_auto_registration_tracks_rebound_names(
        self, app_manager, ipython_shell, supported_app_types
    ):
        mock_mast_aladin, _ = supported_app_types
        ipython_shell.push({"MockMastAladin": mock_mast_aladin})
        ipython_shell.run_cell("viewer = MockMastAladin()")
        original = ipython_shell.user_ns["viewer"]

        ipython_shell.run_cell("viewer = MockMastAladin()")

        assert app_manager.apps["viewer"] is not original
        replacement = ipython_shell.user_ns["viewer"]
        assert app_manager.apps["viewer"] is replacement

    def test_manual_registration_persists_when_namespace_changes(
        self, app_manager, ipython_shell, supported_app_types
    ):
        mock_mast_aladin, _ = supported_app_types
        manual_app = mock_mast_aladin()
        app_manager.register_app(manual_app, "viewer")

        ipython_shell.run_cell("unrelated = object()")

        assert app_manager.apps["viewer"] is manual_app

    def test_manual_registration_takes_precedence_over_auto_registration(
        self, app_manager, ipython_shell, supported_app_types
    ):
        mock_mast_aladin, _ = supported_app_types
        manual_app = mock_mast_aladin()
        app_manager.register_app(manual_app, "viewer")
        ipython_shell.push({"MockMastAladin": mock_mast_aladin})

        ipython_shell.run_cell("viewer = MockMastAladin()")

        assert app_manager.apps["viewer"] is manual_app

    def test_manual_registration_can_override_auto_registration(
        self, app_manager, ipython_shell, supported_app_types
    ):
        mock_mast_aladin, _ = supported_app_types
        ipython_shell.push({"MockMastAladin": mock_mast_aladin})
        ipython_shell.run_cell("viewer = MockMastAladin()")
        manual_app = mock_mast_aladin()

        app_manager.register_app(manual_app, "viewer")

        assert app_manager.apps["viewer"] is manual_app
