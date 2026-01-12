"""Tests for UI prompts."""

from unittest.mock import MagicMock, patch

from mac_setup.models import Category, InstalledPackage, InstallMethod, InstallSource, Package
from mac_setup.ui.prompts import (
    MainMenuChoice,
    UninstallMode,
    confirm,
    prompt_category_selection,
    prompt_main_menu,
    prompt_package_selection,
    prompt_packages_to_uninstall,
    prompt_packages_to_update,
    prompt_preset_name,
    prompt_preset_selection,
    prompt_text,
    prompt_uninstall_mode,
)


class TestMainMenuChoice:
    """Tests for MainMenuChoice enum."""

    def test_enum_values(self) -> None:
        """Test all enum values exist."""
        assert MainMenuChoice.FRESH_SETUP == "fresh_setup"
        assert MainMenuChoice.LOAD_PRESET == "load_preset"
        assert MainMenuChoice.BROWSE == "browse"
        assert MainMenuChoice.UPDATE == "update"
        assert MainMenuChoice.UNINSTALL == "uninstall"
        assert MainMenuChoice.STATUS == "status"
        assert MainMenuChoice.EXIT == "exit"


class TestUninstallMode:
    """Tests for UninstallMode enum."""

    def test_enum_values(self) -> None:
        """Test all enum values exist."""
        assert UninstallMode.STANDARD == "standard"
        assert UninstallMode.CLEAN == "clean"


class TestPromptMainMenu:
    """Tests for prompt_main_menu function."""

    @patch("mac_setup.ui.prompts.questionary.select")
    def test_returns_selected_choice(self, mock_select: MagicMock) -> None:
        """Test that selected choice is returned."""
        mock_select.return_value.ask.return_value = MainMenuChoice.BROWSE
        result = prompt_main_menu()
        assert result == MainMenuChoice.BROWSE

    @patch("mac_setup.ui.prompts.questionary.select")
    def test_returns_exit_on_cancel(self, mock_select: MagicMock) -> None:
        """Test that EXIT is returned when user cancels."""
        mock_select.return_value.ask.return_value = None
        result = prompt_main_menu()
        assert result == MainMenuChoice.EXIT


class TestPromptCategorySelection:
    """Tests for prompt_category_selection function."""

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_returns_selected_categories(self, mock_checkbox: MagicMock) -> None:
        """Test that selected categories are returned."""
        mock_checkbox.return_value.ask.return_value = ["browsers", "editors"]
        categories = [
            Category(id="browsers", name="Browsers", description="", packages=[]),
            Category(id="editors", name="Editors", description="", packages=[]),
        ]
        result = prompt_category_selection(categories)
        assert result == ["browsers", "editors"]

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_returns_none_on_cancel(self, mock_checkbox: MagicMock) -> None:
        """Test that None is returned when user cancels (to go back)."""
        mock_checkbox.return_value.ask.return_value = None
        categories = [
            Category(id="browsers", name="Browsers", description="", packages=[]),
        ]
        result = prompt_category_selection(categories)
        assert result is None

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_preselects_categories(self, mock_checkbox: MagicMock) -> None:
        """Test that preselected categories are marked."""
        mock_checkbox.return_value.ask.return_value = ["browsers"]
        categories = [
            Category(id="browsers", name="Browsers", description="", packages=[]),
            Category(id="editors", name="Editors", description="", packages=[]),
        ]
        prompt_category_selection(categories, preselected={"browsers"})
        # Verify checkbox was called (preselection is internal)
        mock_checkbox.assert_called_once()


class TestPromptPackageSelection:
    """Tests for prompt_package_selection function."""

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_returns_selected_packages(self, mock_checkbox: MagicMock) -> None:
        """Test that selected packages are returned."""
        mock_checkbox.return_value.ask.return_value = ["pkg1", "pkg2"]
        category = Category(
            id="test",
            name="Test",
            description="",
            packages=[
                Package(id="pkg1", name="Package 1", description="", method=InstallMethod.FORMULA),
                Package(id="pkg2", name="Package 2", description="", method=InstallMethod.CASK),
            ],
        )
        result = prompt_package_selection(category)
        assert result == ["pkg1", "pkg2"]

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_returns_none_on_cancel(self, mock_checkbox: MagicMock) -> None:
        """Test that None is returned when user cancels (to go back)."""
        mock_checkbox.return_value.ask.return_value = None
        category = Category(
            id="test",
            name="Test",
            description="",
            packages=[
                Package(id="pkg1", name="Package 1", description="", method=InstallMethod.FORMULA),
            ],
        )
        result = prompt_package_selection(category)
        assert result is None

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_preselects_packages(self, mock_checkbox: MagicMock) -> None:
        """Test preselected packages."""
        mock_checkbox.return_value.ask.return_value = ["pkg1"]
        category = Category(
            id="test",
            name="Test",
            description="",
            packages=[
                Package(id="pkg1", name="Package 1", description="", method=InstallMethod.FORMULA),
            ],
        )
        prompt_package_selection(category, preselected={"pkg1"})
        mock_checkbox.assert_called_once()

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_shows_installed_status(self, mock_checkbox: MagicMock) -> None:
        """Test that installed packages are marked."""
        mock_checkbox.return_value.ask.return_value = []
        category = Category(
            id="test",
            name="Test",
            description="",
            packages=[
                Package(id="pkg1", name="Package 1", description="", method=InstallMethod.FORMULA),
            ],
        )
        prompt_package_selection(category, installed={"pkg1"})
        mock_checkbox.assert_called_once()


class TestPromptPackagesToUninstall:
    """Tests for prompt_packages_to_uninstall function."""

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_returns_selected_packages(self, mock_checkbox: MagicMock) -> None:
        """Test that selected packages are returned."""
        mock_checkbox.return_value.ask.return_value = ["pkg1"]
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
            InstalledPackage(
                id="pkg2", name="Package 2", method=InstallMethod.CASK,
                source=InstallSource.MAC_SETUP
            ),
        ]
        result = prompt_packages_to_uninstall(packages)
        assert result == ["pkg1"]

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_returns_none_on_cancel(self, mock_checkbox: MagicMock) -> None:
        """Test that None is returned when user cancels (to go back)."""
        mock_checkbox.return_value.ask.return_value = None
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        result = prompt_packages_to_uninstall(packages)
        assert result is None


class TestPromptPackagesToUpdate:
    """Tests for prompt_packages_to_update function."""

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_returns_selected_packages(self, mock_checkbox: MagicMock) -> None:
        """Test that selected packages are returned."""
        mock_checkbox.return_value.ask.return_value = ["pkg1"]
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP, version="1.0"
            ),
        ]
        result = prompt_packages_to_update(packages, {"pkg1": "2.0"})
        assert result == ["pkg1"]

    @patch("mac_setup.ui.prompts.questionary.checkbox")
    def test_returns_none_on_cancel(self, mock_checkbox: MagicMock) -> None:
        """Test that None is returned when user cancels (to go back)."""
        mock_checkbox.return_value.ask.return_value = None
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        result = prompt_packages_to_update(packages, {})
        assert result is None


class TestPromptPresetSelection:
    """Tests for prompt_preset_selection function."""

    @patch("mac_setup.ui.prompts.questionary.select")
    def test_returns_selected_preset(self, mock_select: MagicMock) -> None:
        """Test that selected preset is returned."""
        mock_select.return_value.ask.return_value = "minimal"
        presets = [("minimal", "Minimal setup"), ("developer", "Developer setup")]
        result = prompt_preset_selection(presets)
        assert result == "minimal"

    @patch("mac_setup.ui.prompts.questionary.select")
    def test_returns_none_on_cancel(self, mock_select: MagicMock) -> None:
        """Test that None is returned when user cancels."""
        mock_select.return_value.ask.return_value = None
        presets = [("minimal", "Minimal setup")]
        result = prompt_preset_selection(presets)
        assert result is None


class TestPromptPresetName:
    """Tests for prompt_preset_name function."""

    @patch("mac_setup.ui.prompts.questionary.text")
    def test_returns_trimmed_name(self, mock_text: MagicMock) -> None:
        """Test that preset name is trimmed."""
        mock_text.return_value.ask.return_value = "  my preset  "
        result = prompt_preset_name()
        assert result == "my preset"

    @patch("mac_setup.ui.prompts.questionary.text")
    def test_returns_none_on_cancel(self, mock_text: MagicMock) -> None:
        """Test that None is returned when user cancels."""
        mock_text.return_value.ask.return_value = None
        result = prompt_preset_name()
        assert result is None


class TestPromptUninstallMode:
    """Tests for prompt_uninstall_mode function."""

    @patch("mac_setup.ui.prompts.questionary.select")
    def test_returns_selected_mode(self, mock_select: MagicMock) -> None:
        """Test that selected mode is returned."""
        mock_select.return_value.ask.return_value = UninstallMode.CLEAN
        result = prompt_uninstall_mode()
        assert result == UninstallMode.CLEAN

    @patch("mac_setup.ui.prompts.questionary.select")
    def test_returns_none_on_cancel(self, mock_select: MagicMock) -> None:
        """Test that None is returned when user cancels (to go back)."""
        mock_select.return_value.ask.return_value = None
        result = prompt_uninstall_mode()
        assert result is None


class TestConfirm:
    """Tests for confirm function."""

    @patch("mac_setup.ui.prompts.questionary.confirm")
    def test_returns_true_on_confirm(self, mock_confirm: MagicMock) -> None:
        """Test that True is returned on confirmation."""
        mock_confirm.return_value.ask.return_value = True
        result = confirm("Are you sure?")
        assert result is True

    @patch("mac_setup.ui.prompts.questionary.confirm")
    def test_returns_false_on_decline(self, mock_confirm: MagicMock) -> None:
        """Test that False is returned on decline."""
        mock_confirm.return_value.ask.return_value = False
        result = confirm("Are you sure?")
        assert result is False

    @patch("mac_setup.ui.prompts.questionary.confirm")
    def test_returns_false_on_cancel(self, mock_confirm: MagicMock) -> None:
        """Test that False is returned when user cancels."""
        mock_confirm.return_value.ask.return_value = None
        result = confirm("Are you sure?")
        assert result is False


class TestPromptText:
    """Tests for prompt_text function."""

    @patch("mac_setup.ui.prompts.questionary.text")
    def test_returns_entered_text(self, mock_text: MagicMock) -> None:
        """Test that entered text is returned."""
        mock_text.return_value.ask.return_value = "user input"
        result = prompt_text("Enter text:")
        assert result == "user input"

    @patch("mac_setup.ui.prompts.questionary.text")
    def test_returns_none_on_cancel(self, mock_text: MagicMock) -> None:
        """Test that None is returned when user cancels."""
        mock_text.return_value.ask.return_value = None
        result = prompt_text("Enter text:")
        assert result is None
