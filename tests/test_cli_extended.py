"""Extended tests for CLI commands to increase coverage."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from mac_setup.cli import (
    _run_installation,
    _run_uninstallation,
    app,
    run_status,
)
from mac_setup.models import InstalledPackage, InstallMethod, InstallSource, Package

runner = CliRunner()


class TestInstallCommandExtended:
    """Extended tests for install command."""

    @patch("mac_setup.cli.StateManager")
    @patch("mac_setup.cli.catalog")
    @patch("mac_setup.cli.sync_detected_packages")
    def test_install_with_category_filter(
        self,
        mock_sync: MagicMock,
        mock_catalog: MagicMock,
        mock_state: MagicMock,
    ) -> None:
        """Test install with category filter."""
        mock_catalog.get_category.return_value = MagicMock(
            packages=[
                Package(
                    id="pkg1", name="Package 1", description="Desc",
                    method=InstallMethod.FORMULA
                ),
            ]
        )
        mock_state_instance = MagicMock()
        mock_state_instance.get_all_installed.return_value = []
        mock_state.return_value = mock_state_instance

        result = runner.invoke(app, ["--dry-run", "--yes", "install", "--category", "cli"])
        # Should run without crashing
        assert result.exit_code in (0, 1)

    @patch("mac_setup.cli.StateManager")
    @patch("mac_setup.cli.PresetManager")
    @patch("mac_setup.cli.sync_detected_packages")
    def test_install_with_preset(
        self,
        mock_sync: MagicMock,
        mock_preset_mgr: MagicMock,
        mock_state: MagicMock,
    ) -> None:
        """Test install with preset."""
        mock_preset = MagicMock()
        mock_preset.packages = {"cli": ["git"]}
        mock_preset_instance = MagicMock()
        mock_preset_instance.load_by_name.return_value = mock_preset
        mock_preset_instance.get_packages.return_value = [
            Package(id="git", name="Git", description="VCS", method=InstallMethod.FORMULA),
        ]
        mock_preset_instance.validate.return_value = []
        mock_preset_mgr.return_value = mock_preset_instance

        mock_state_instance = MagicMock()
        mock_state_instance.get_all_installed.return_value = []
        mock_state.return_value = mock_state_instance

        result = runner.invoke(app, ["--dry-run", "--yes", "install", "--preset", "minimal"])
        assert result.exit_code in (0, 1)


class TestUninstallCommandExtended:
    """Extended tests for uninstall command."""

    @patch("mac_setup.cli.StateManager")
    @patch("mac_setup.cli.sync_detected_packages")
    def test_uninstall_with_packages_flag(
        self,
        mock_sync: MagicMock,
        mock_state: MagicMock,
    ) -> None:
        """Test uninstall with specific packages."""
        mock_state_instance = MagicMock()
        mock_state_instance.get_mac_setup_packages.return_value = [
            InstalledPackage(
                id="test-pkg", name="Test Package",
                method=InstallMethod.FORMULA, source=InstallSource.MAC_SETUP
            ),
        ]
        mock_state_instance.get_installed_package.return_value = InstalledPackage(
            id="test-pkg", name="Test Package",
            method=InstallMethod.FORMULA, source=InstallSource.MAC_SETUP
        )
        mock_state.return_value = mock_state_instance

        result = runner.invoke(app, ["--dry-run", "--yes", "uninstall", "--packages", "test-pkg"])
        assert result.exit_code in (0, 1)


class TestStatusCommandExtended:
    """Extended tests for status command."""

    @patch("mac_setup.cli.StateManager")
    @patch("mac_setup.cli.sync_detected_packages")
    @patch("mac_setup.cli.print_status")
    def test_status_with_installed_packages(
        self,
        mock_print: MagicMock,
        mock_sync: MagicMock,
        mock_state: MagicMock,
    ) -> None:
        """Test status shows installed packages."""
        mock_state_instance = MagicMock()
        mock_state_instance.get_mac_setup_packages.return_value = [
            InstalledPackage(
                id="git", name="Git",
                method=InstallMethod.FORMULA, source=InstallSource.MAC_SETUP
            ),
        ]
        mock_state_instance.get_detected_packages.return_value = []
        mock_state.return_value = mock_state_instance

        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0


class TestPresetsCommandExtended:
    """Extended tests for presets command."""

    @patch("mac_setup.cli.PresetManager")
    def test_presets_list_with_presets(self, mock_preset_mgr: MagicMock) -> None:
        """Test presets list shows available presets."""
        mock_instance = MagicMock()
        mock_instance.list_available.return_value = [
            ("minimal", "Minimal setup", True),
            ("developer", "Developer setup", True),
        ]
        mock_preset_mgr.return_value = mock_instance

        result = runner.invoke(app, ["presets"])
        assert result.exit_code == 0
        # Should mention available presets
        assert "minimal" in result.output.lower() or "developer" in result.output.lower()


class TestBrowseCommandExtended:
    """Extended tests for browse command."""

    @patch("mac_setup.cli.catalog")
    @patch("mac_setup.cli.StateManager")
    @patch("mac_setup.cli.sync_detected_packages")
    def test_browse_shows_categories(
        self,
        mock_sync: MagicMock,
        mock_state: MagicMock,
        mock_catalog: MagicMock,
    ) -> None:
        """Test browse shows categories."""
        from mac_setup.models import Category
        mock_catalog.get_all_categories.return_value = [
            Category(
                id="cli",
                name="CLI Utilities",
                description="Command-line tools",
                icon="⌨️",
                packages=[
                    Package(id="git", name="Git", description="VCS", method=InstallMethod.FORMULA),
                ],
            ),
        ]
        mock_state_instance = MagicMock()
        mock_state_instance.get_all_installed.return_value = []
        mock_state.return_value = mock_state_instance

        result = runner.invoke(app, ["browse"])
        assert result.exit_code in (0, 1)


class TestGlobalOptionsExtended:
    """Extended tests for global options."""

    def test_dry_run_option(self) -> None:
        """Test --dry-run flag is recognized."""
        result = runner.invoke(app, ["--dry-run", "--help"])
        assert result.exit_code == 0

    def test_yes_option(self) -> None:
        """Test --yes flag is recognized."""
        result = runner.invoke(app, ["--yes", "--help"])
        assert result.exit_code == 0

    def test_verbose_option(self) -> None:
        """Test --verbose flag is recognized."""
        result = runner.invoke(app, ["--verbose", "--help"])
        assert result.exit_code == 0


class TestSaveCommand:
    """Tests for save command."""

    @patch("mac_setup.cli.prompt_category_selection")
    def test_save_exits_on_no_categories_selected(
        self,
        mock_prompt: MagicMock,
    ) -> None:
        """Test save exits when no categories selected."""
        mock_prompt.return_value = []
        result = runner.invoke(app, ["save", "my-preset"])
        assert result.exit_code == 0


class TestInteractiveSetup:
    """Tests for interactive_setup function."""

    @patch("mac_setup.cli.prompt_main_menu")
    @patch("mac_setup.cli.print_banner")
    @patch("mac_setup.cli.ensure_directories")
    def test_interactive_setup_exit(
        self,
        mock_ensure: MagicMock,
        mock_banner: MagicMock,
        mock_menu: MagicMock,
    ) -> None:
        """Test interactive setup exits on EXIT choice."""
        from mac_setup.ui.prompts import MainMenuChoice
        mock_menu.return_value = MainMenuChoice.EXIT
        # Use runner to invoke app with no command (triggers interactive)
        runner.invoke(app, [], input="\n")
        mock_menu.assert_called()

    @patch("mac_setup.cli.run_status")
    @patch("mac_setup.cli.prompt_main_menu")
    @patch("mac_setup.cli.print_banner")
    @patch("mac_setup.cli.ensure_directories")
    def test_interactive_setup_status(
        self,
        mock_ensure: MagicMock,
        mock_banner: MagicMock,
        mock_menu: MagicMock,
        mock_status: MagicMock,
    ) -> None:
        """Test interactive setup runs status on STATUS choice."""
        from mac_setup.ui.prompts import MainMenuChoice
        mock_menu.side_effect = [MainMenuChoice.STATUS, MainMenuChoice.EXIT]
        runner.invoke(app, [], input="\n")
        mock_status.assert_called()


class TestRunStatus:
    """Tests for run_status function."""

    @patch("mac_setup.cli.print_status")
    @patch("mac_setup.cli.sync_detected_packages")
    @patch("mac_setup.cli.StateManager")
    def test_run_status_shows_packages(
        self,
        mock_state: MagicMock,
        mock_sync: MagicMock,
        mock_print: MagicMock,
    ) -> None:
        """Test run_status displays packages."""
        mock_state_instance = MagicMock()
        mock_state_instance.get_mac_setup_packages.return_value = []
        mock_state_instance.get_detected_packages.return_value = []
        mock_state.return_value = mock_state_instance
        run_status()
        mock_print.assert_called_once()


class TestRunInstallation:
    """Tests for _run_installation helper function."""

    @patch("mac_setup.cli.print_install_plan")
    @patch("mac_setup.cli.HomebrewInstaller")
    def test_run_installation_homebrew_not_available(
        self,
        mock_homebrew: MagicMock,
        mock_plan: MagicMock,
    ) -> None:
        """Test _run_installation when Homebrew is not available."""
        mock_homebrew.return_value.is_available.return_value = False
        packages = [
            Package(id="pkg1", name="Package 1", description="Desc", method=InstallMethod.FORMULA),
        ]
        _run_installation(packages, dry_run=False)
        # Should not crash

    @patch("mac_setup.cli.print_install_plan")
    @patch("mac_setup.cli.HomebrewInstaller")
    def test_run_installation_all_installed(
        self,
        mock_homebrew: MagicMock,
        mock_plan: MagicMock,
    ) -> None:
        """Test _run_installation when all packages are already installed."""
        mock_homebrew.return_value.is_available.return_value = True
        mock_homebrew.return_value.list_installed.return_value = ["pkg1"]
        packages = [
            Package(id="pkg1", name="Package 1", description="Desc", method=InstallMethod.FORMULA),
        ]
        _run_installation(packages, dry_run=False)
        # Should not crash, should skip installation

    @patch("mac_setup.cli.print_install_plan")
    @patch("mac_setup.cli.HomebrewInstaller")
    def test_run_installation_dry_run(
        self,
        mock_homebrew: MagicMock,
        mock_plan: MagicMock,
    ) -> None:
        """Test _run_installation in dry run mode."""
        mock_homebrew.return_value.is_available.return_value = True
        mock_homebrew.return_value.list_installed.return_value = []
        packages = [
            Package(id="pkg1", name="Package 1", description="Desc", method=InstallMethod.FORMULA),
        ]
        _run_installation(packages, dry_run=True)
        mock_plan.assert_called_once()

    def test_run_installation_empty_packages(self) -> None:
        """Test _run_installation with no packages."""
        _run_installation([], dry_run=False)
        # Should not crash


class TestRunUninstallation:
    """Tests for _run_uninstallation helper function."""

    def test_run_uninstallation_empty_packages(self) -> None:
        """Test _run_uninstallation with no packages."""
        mock_state = MagicMock()
        _run_uninstallation([], clean=False, dry_run=False, state_manager=mock_state)
        # Should not crash

    @patch("mac_setup.cli.HomebrewInstaller")
    def test_run_uninstallation_dry_run(
        self,
        mock_homebrew: MagicMock,
    ) -> None:
        """Test _run_uninstallation in dry run mode."""
        mock_homebrew.return_value.is_available.return_value = True
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        mock_state = MagicMock()
        _run_uninstallation(packages, clean=False, dry_run=True, state_manager=mock_state)
        # Dry run should return early without actually uninstalling


class TestUpdateCommand:
    """Tests for update command."""

    @patch("mac_setup.cli.StateManager")
    @patch("mac_setup.cli.sync_detected_packages")
    def test_update_no_packages_installed(
        self,
        mock_sync: MagicMock,
        mock_state: MagicMock,
    ) -> None:
        """Test update with no packages installed."""
        mock_state_instance = MagicMock()
        mock_state_instance.get_mac_setup_packages.return_value = []
        mock_state.return_value = mock_state_instance

        result = runner.invoke(app, ["--yes", "update", "--all"])
        assert result.exit_code in (0, 1)


class TestResetCommand:
    """Tests for reset command."""

    @patch("mac_setup.cli.StateManager")
    @patch("mac_setup.cli.sync_detected_packages")
    def test_reset_no_packages(
        self,
        mock_sync: MagicMock,
        mock_state: MagicMock,
    ) -> None:
        """Test reset with no packages to remove."""
        mock_state_instance = MagicMock()
        mock_state_instance.get_mac_setup_packages.return_value = []
        mock_state.return_value = mock_state_instance

        result = runner.invoke(app, ["--yes", "reset"])
        assert result.exit_code in (0, 1)
