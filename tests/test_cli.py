"""Tests for CLI commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from mac_setup.cli import app

runner = CliRunner()


class TestCLIBasic:
    """Basic CLI tests."""

    def test_version_option(self) -> None:
        """Test --version shows version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "mac-setup" in result.stdout
        assert "v" in result.stdout

    def test_help_option(self) -> None:
        """Test --help shows help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Interactive macOS" in result.stdout

    def test_browse_command_exists(self) -> None:
        """Test browse command exists."""
        result = runner.invoke(app, ["browse", "--help"])
        assert result.exit_code == 0
        assert "Browse available packages" in result.stdout

    def test_install_command_exists(self) -> None:
        """Test install command exists."""
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0
        assert "--preset" in result.stdout

    def test_status_command_exists(self) -> None:
        """Test status command exists."""
        result = runner.invoke(app, ["status", "--help"])
        assert result.exit_code == 0

    def test_presets_command_exists(self) -> None:
        """Test presets command exists."""
        result = runner.invoke(app, ["presets", "--help"])
        assert result.exit_code == 0

    def test_uninstall_command_exists(self) -> None:
        """Test uninstall command exists."""
        result = runner.invoke(app, ["uninstall", "--help"])
        assert result.exit_code == 0
        assert "--packages" in result.stdout
        assert "--clean" in result.stdout

    def test_reset_command_exists(self) -> None:
        """Test reset command exists."""
        result = runner.invoke(app, ["reset", "--help"])
        assert result.exit_code == 0
        assert "--confirm" in result.stdout


class TestStatusCommand:
    """Tests for status command."""

    @patch("mac_setup.cli.HomebrewInstaller")
    @patch("mac_setup.cli.MASInstaller")
    @patch("mac_setup.cli.StateManager")
    def test_status_shows_packages(
        self,
        mock_state: MagicMock,
        mock_mas: MagicMock,
        mock_homebrew: MagicMock,
    ) -> None:
        """Test status command shows packages."""
        # Setup mocks
        mock_homebrew_instance = MagicMock()
        mock_homebrew_instance.is_available.return_value = True
        mock_homebrew_instance.list_installed.return_value = []
        mock_homebrew.return_value = mock_homebrew_instance

        mock_mas_instance = MagicMock()
        mock_mas_instance.is_available.return_value = True
        mock_mas_instance.list_installed_ids.return_value = []
        mock_mas.return_value = mock_mas_instance

        mock_state_instance = MagicMock()
        mock_state_instance.get_mac_setup_packages.return_value = []
        mock_state_instance.get_detected_packages.return_value = []
        mock_state.return_value = mock_state_instance

        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0


class TestPresetsCommand:
    """Tests for presets command."""

    @patch("mac_setup.cli.PresetManager")
    def test_presets_lists_available(self, mock_manager: MagicMock) -> None:
        """Test presets command lists available presets."""
        mock_instance = MagicMock()
        mock_instance.list_available.return_value = [
            ("Minimal", "Essential tools", True),
            ("Developer", "Full-stack setup", True),
        ]
        mock_manager.return_value = mock_instance

        result = runner.invoke(app, ["presets"])
        assert result.exit_code == 0
        assert "Minimal" in result.stdout
        assert "Developer" in result.stdout

    @patch("mac_setup.cli.PresetManager")
    def test_presets_empty(self, mock_manager: MagicMock) -> None:
        """Test presets command with no presets."""
        mock_instance = MagicMock()
        mock_instance.list_available.return_value = []
        mock_manager.return_value = mock_instance

        result = runner.invoke(app, ["presets"])
        assert result.exit_code == 0
        assert "No presets" in result.stdout


class TestInstallCommand:
    """Tests for install command."""

    @patch("mac_setup.cli.HomebrewInstaller")
    @patch("mac_setup.cli.load_preset")
    @patch("mac_setup.cli.PresetManager")
    def test_install_dry_run(
        self,
        mock_manager: MagicMock,
        mock_load: MagicMock,
        mock_homebrew: MagicMock,
    ) -> None:
        """Test install with dry-run doesn't execute."""
        from mac_setup.models import Preset

        mock_homebrew_instance = MagicMock()
        mock_homebrew_instance.is_available.return_value = True
        mock_homebrew_instance.list_installed.return_value = []
        mock_homebrew.return_value = mock_homebrew_instance

        mock_load.return_value = Preset(
            name="Test",
            packages={"browsers": ["google-chrome"]},
        )

        mock_manager_instance = MagicMock()
        mock_manager_instance.get_packages.return_value = []
        mock_manager.return_value = mock_manager_instance

        result = runner.invoke(app, ["--dry-run", "install", "--preset", "test"])
        assert result.exit_code == 0
        # Verify install was not actually called
        mock_homebrew_instance.install.assert_not_called()

    def test_install_preset_not_found(self) -> None:
        """Test install with non-existent preset."""
        result = runner.invoke(app, ["install", "--preset", "nonexistent-preset-xyz"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()


class TestUninstallCommand:
    """Tests for uninstall command."""

    @patch("mac_setup.cli.StateManager")
    def test_uninstall_no_packages(self, mock_state: MagicMock) -> None:
        """Test uninstall with no tracked packages."""
        mock_instance = MagicMock()
        mock_instance.get_all_installed.return_value = []
        mock_state.return_value = mock_instance

        result = runner.invoke(app, ["uninstall", "--packages", "nonexistent"])
        assert result.exit_code == 0
        assert "No tracked packages" in result.stdout or "warning" in result.stdout.lower()


class TestResetCommand:
    """Tests for reset command."""

    @patch("mac_setup.cli.StateManager")
    def test_reset_no_packages(self, mock_state: MagicMock) -> None:
        """Test reset with no packages."""
        mock_instance = MagicMock()
        mock_instance.get_mac_setup_packages.return_value = []
        mock_state.return_value = mock_instance

        result = runner.invoke(app, ["reset"])
        assert result.exit_code == 0
        assert "No mac-setup" in result.stdout


class TestDryRunMode:
    """Tests for dry-run mode."""

    @patch("mac_setup.cli.HomebrewInstaller")
    @patch("mac_setup.cli.StateManager")
    @patch("mac_setup.cli.confirm")
    def test_dry_run_prevents_changes(
        self,
        mock_confirm: MagicMock,
        mock_state: MagicMock,
        mock_homebrew: MagicMock,
    ) -> None:
        """Test that dry-run mode prevents actual changes."""
        mock_homebrew_instance = MagicMock()
        mock_homebrew_instance.is_available.return_value = True
        mock_homebrew_instance.list_installed.return_value = ["existing-pkg"]
        mock_homebrew.return_value = mock_homebrew_instance

        mock_state_instance = MagicMock()
        mock_state.return_value = mock_state_instance

        # Run with dry-run
        result = runner.invoke(app, ["--dry-run", "browse"])
        assert result.exit_code == 0

        # Verify no install was called
        mock_homebrew_instance.install.assert_not_called()


class TestBrowseCommand:
    """Tests for browse command."""

    @patch("mac_setup.cli.HomebrewInstaller")
    def test_browse_shows_categories(self, mock_homebrew: MagicMock) -> None:
        """Test browse command shows categories."""
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        mock_instance.list_installed.return_value = []
        mock_homebrew.return_value = mock_instance

        result = runner.invoke(app, ["browse"])
        assert result.exit_code == 0
        # Should show some categories/packages
        assert "Browsers" in result.stdout or "Chrome" in result.stdout


class TestGlobalOptions:
    """Tests for global options."""

    def test_quiet_option(self) -> None:
        """Test --quiet option is accepted."""
        result = runner.invoke(app, ["--quiet", "status", "--help"])
        assert result.exit_code == 0

    def test_verbose_option(self) -> None:
        """Test --verbose option is accepted."""
        result = runner.invoke(app, ["--verbose", "status", "--help"])
        assert result.exit_code == 0

    def test_no_color_option(self) -> None:
        """Test --no-color option is accepted."""
        result = runner.invoke(app, ["--no-color", "status", "--help"])
        assert result.exit_code == 0

    def test_yes_option(self) -> None:
        """Test --yes option is accepted."""
        result = runner.invoke(app, ["--yes", "status", "--help"])
        assert result.exit_code == 0
