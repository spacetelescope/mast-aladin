import pytest
from unittest.mock import Mock, MagicMock
from mast_aladin.managers.app_manager import AppManager


class TestAppManager:
    """Test suite for AppManager class."""

    @pytest.fixture
    def mock_mast_manager(self):
        """Create a mock MastManager instance."""
        return Mock()

    @pytest.fixture
    def app_manager(self, mock_mast_manager):
        """Create an AppManager instance with a mock MastManager."""
        return AppManager(mock_mast_manager)

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
        """Test registering multiple apps."""
        mock_app1 = Mock()
        mock_app2 = Mock()
        mock_app3 = Mock()

        # Test with underscores
        app_manager.register_app(mock_app1, "mast_aladin_1")
        assert "mast_aladin_1" in app_manager.apps

        # Test with hyphens
        app_manager.register_app(mock_app2, "imviz-viewer")
        assert "imviz-viewer" in app_manager.apps

        # Test with just alphanumeric
        app_manager.register_app(mock_app3, "app123")
        assert "app123" in app_manager.apps

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

    def test_mast_manager_reference_preserved(self, app_manager, mock_mast_manager):
        """Test that MastManager reference is preserved after operations."""
        mock_app = Mock()
        app_manager.register_app(mock_app, "test_app")

        # Reference should still be the same
        assert app_manager._mast_manager is mock_mast_manager
