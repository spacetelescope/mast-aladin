import pytest
from unittest.mock import Mock, patch, MagicMock
from mast_aladin.managers.mast_manager import MastManager


class TestMastManager:
    """Test suite for MastManager class."""

    def test_initialization(self):
        """Test that MastManager initializes correctly."""
        mm = MastManager()
        assert mm._app_manager is not None

    def test_register_app(self):
        """Test registering an app through MastManager."""
        mm = MastManager()
        mock_app = Mock()

        mm.register_app(mock_app, "test_app")

        assert "test_app" in mm.apps
        assert mm.apps["test_app"] is mock_app

    def test_register_app_multiple(self):
        """Test registering multiple mock app objects."""
        mm = MastManager()

        # Mock different app types
        mock_aladin = MagicMock(name="aladin")
        mock_imviz = MagicMock(name="imviz")
        mock_custom = MagicMock(name="custom_app")

        mm.register_app(mock_aladin, "aladin")
        mm.register_app(mock_imviz, "imviz")
        mm.register_app(mock_custom, "custom")

        assert len(mm.apps) == 3
        assert mm.apps["aladin"] is mock_aladin
        assert mm.apps["imviz"] is mock_imviz
        assert mm.apps["custom"] is mock_custom

    def test_register_app_duplicate_id_raises_error(self):
        """Test that registering with duplicate ID raises ValueError."""
        mm = MastManager()
        mock_app1 = Mock()
        mock_app2 = Mock()

        mm.register_app(mock_app1, "duplicate")

        with pytest.raises(ValueError) as exc_info:
            mm.register_app(mock_app2, "duplicate")

        assert "duplicate" in str(exc_info.value)
