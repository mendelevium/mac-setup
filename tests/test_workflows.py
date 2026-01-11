"""Tests for end-to-end workflows (all subprocess calls mocked)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mac_setup.installers import HomebrewInstaller
from mac_setup.installers.base import InstallResult, InstallStatus
from mac_setup.models import InstallMethod, InstallSource, Package
from mac_setup.state import StateManager


class TestInstallationWorkflow:
    """Tests for the installation workflow."""

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_skips_already_installed(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test that installation skips already installed packages."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        # Return google-chrome as already installed
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas
            MagicMock(returncode=0, stdout="google-chrome\n"),  # casks
        ]

        installer = HomebrewInstaller()
        result = installer.install("google-chrome", InstallMethod.CASK)

        assert result.status == InstallStatus.ALREADY_INSTALLED

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_new_package(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test installing a new package."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas
            MagicMock(returncode=0, stdout=""),  # casks (not installed)
            MagicMock(returncode=0, stdout=""),  # install success
            MagicMock(returncode=0, stdout=""),  # formulas (for get_version)
            MagicMock(returncode=0, stdout="new-package"),  # casks (now installed)
            MagicMock(returncode=0, stdout='{"casks":[{"token":"new-package","installed":"2.0"}]}'),  # info
        ]

        installer = HomebrewInstaller()
        result = installer.install("new-package", InstallMethod.CASK)

        assert result.status == InstallStatus.SUCCESS
        assert result.version == "2.0"

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_failure_handling(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test handling of installation failures."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas
            MagicMock(returncode=0, stdout=""),  # casks
            MagicMock(returncode=1, stderr="Error: Package not found"),  # install failed
        ]

        installer = HomebrewInstaller()
        result = installer.install("bad-package", InstallMethod.CASK)

        assert result.status == InstallStatus.FAILED
        assert "not found" in result.message.lower()

    def test_dry_run_does_not_install(self) -> None:
        """Test that dry run mode doesn't actually install."""
        with patch("shutil.which") as mock_which:
            with patch("subprocess.run") as mock_run:
                mock_which.return_value = "/opt/homebrew/bin/brew"
                mock_run.side_effect = [
                    MagicMock(returncode=0, stdout=""),
                    MagicMock(returncode=0, stdout=""),
                ]

                installer = HomebrewInstaller()
                result = installer.install("test-pkg", InstallMethod.CASK, dry_run=True)

                assert result.status == InstallStatus.SKIPPED
                # Verify install command was not run
                install_calls = [
                    call for call in mock_run.call_args_list
                    if "install" in str(call)
                ]
                # Only the list calls should happen, not install
                assert len([c for c in mock_run.call_args_list if "install" in str(c[0][0])]) == 0


class TestUninstallWorkflow:
    """Tests for the uninstall workflow."""

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_uninstall_installed_package(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test uninstalling an installed package."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas
            MagicMock(returncode=0, stdout="test-pkg\n"),  # casks (installed)
            MagicMock(returncode=0, stdout=""),  # uninstall success
        ]

        installer = HomebrewInstaller()
        result = installer.uninstall("test-pkg", InstallMethod.CASK)

        assert result.status == InstallStatus.SUCCESS

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_uninstall_not_installed(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test uninstalling a package that isn't installed."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas
            MagicMock(returncode=0, stdout=""),  # casks (not installed)
        ]

        installer = HomebrewInstaller()
        result = installer.uninstall("not-installed", InstallMethod.CASK)

        assert result.status == InstallStatus.SKIPPED

    def test_uninstall_dry_run(self) -> None:
        """Test that dry run doesn't uninstall."""
        with patch("shutil.which") as mock_which:
            with patch("subprocess.run") as mock_run:
                mock_which.return_value = "/opt/homebrew/bin/brew"
                mock_run.side_effect = [
                    MagicMock(returncode=0, stdout=""),
                    MagicMock(returncode=0, stdout="test-pkg\n"),
                ]

                installer = HomebrewInstaller()
                result = installer.uninstall("test-pkg", InstallMethod.CASK, dry_run=True)

                assert result.status == InstallStatus.SKIPPED
                # Verify uninstall was not called
                uninstall_calls = [
                    c for c in mock_run.call_args_list
                    if "uninstall" in str(c)
                ]
                assert len(uninstall_calls) == 0


class TestStateTrackingWorkflow:
    """Tests for state tracking during workflows."""

    def test_install_updates_state(self, tmp_path: Path) -> None:
        """Test that successful install updates state."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        pkg = Package(
            id="test-pkg",
            name="Test Package",
            description="A test",
            method=InstallMethod.CASK,
        )

        manager.add_installed_package(pkg, InstallSource.MAC_SETUP, version="1.0.0")

        # Verify state was updated
        assert manager.is_tracked("test-pkg")
        installed = manager.get_installed_package("test-pkg")
        assert installed is not None
        assert installed.version == "1.0.0"
        assert installed.source == InstallSource.MAC_SETUP

    def test_uninstall_updates_state(self, tmp_path: Path) -> None:
        """Test that successful uninstall updates state."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        # First add a package
        pkg = Package(
            id="test-pkg",
            name="Test Package",
            description="A test",
            method=InstallMethod.CASK,
        )
        manager.add_installed_package(pkg, InstallSource.MAC_SETUP)
        assert manager.is_tracked("test-pkg")

        # Then remove it
        manager.remove_installed_package("test-pkg")
        assert not manager.is_tracked("test-pkg")

    def test_state_persists_across_sessions(self, tmp_path: Path) -> None:
        """Test that state persists when reloading."""
        state_file = tmp_path / "state.json"

        # Session 1: Add package
        manager1 = StateManager(state_file)
        pkg = Package(
            id="persistent-pkg",
            name="Persistent",
            description="Should persist",
            method=InstallMethod.FORMULA,
        )
        manager1.add_installed_package(pkg, InstallSource.MAC_SETUP)

        # Session 2: Load and verify
        manager2 = StateManager(state_file)
        assert manager2.is_tracked("persistent-pkg")


class TestIdempotentBehavior:
    """Tests for idempotent behavior."""

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_same_package_twice(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test that installing same package twice is handled correctly."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        # First install - not installed, includes version fetch after install
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas
            MagicMock(returncode=0, stdout=""),  # casks
            MagicMock(returncode=0, stdout=""),  # install success
            MagicMock(returncode=0, stdout=""),  # formulas (for get_version)
            MagicMock(returncode=0, stdout="new-pkg"),  # casks (now installed)
            MagicMock(returncode=0, stdout='{"casks":[{"token":"new-pkg","installed":"1.0"}]}'),  # info
        ]

        installer = HomebrewInstaller()
        result1 = installer.install("new-pkg", InstallMethod.CASK)
        assert result1.status == InstallStatus.SUCCESS

        # Reset mock for second install
        installer._installed_casks = None
        installer._installed_formulas = None

        # Second install - now installed
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),
            MagicMock(returncode=0, stdout="new-pkg\n"),  # now installed
        ]

        result2 = installer.install("new-pkg", InstallMethod.CASK)
        assert result2.status == InstallStatus.ALREADY_INSTALLED


class TestPresetWorkflow:
    """Tests for preset-based workflows."""

    def test_load_and_install_from_preset(self, tmp_path: Path) -> None:
        """Test loading packages from a preset."""
        from mac_setup.models import Preset
        from mac_setup.presets.manager import PresetManager

        # Create a preset
        preset = Preset(
            name="Test Workflow",
            packages={
                "browsers": ["google-chrome"],
                "cli": ["git", "ripgrep"],
            },
        )

        manager = PresetManager()
        packages = manager.get_packages(preset)

        # Verify packages were extracted
        assert len(packages) == 3
        package_ids = [p.id for p in packages]
        assert "google-chrome" in package_ids
        assert "git" in package_ids
        assert "ripgrep" in package_ids

    def test_validate_preset_before_install(self) -> None:
        """Test that invalid packages are caught during validation."""
        from mac_setup.models import Preset
        from mac_setup.presets.manager import PresetManager

        preset = Preset(
            name="Invalid Preset",
            packages={
                "browsers": ["google-chrome", "fake-browser-xyz"],
            },
        )

        manager = PresetManager()
        warnings = manager.validate(preset)

        assert len(warnings) == 1
        assert "fake-browser-xyz" in warnings[0]


class TestErrorRecovery:
    """Tests for error recovery in workflows."""

    @patch("shutil.which")
    def test_homebrew_not_available(self, mock_which: MagicMock) -> None:
        """Test handling when Homebrew is not installed."""
        mock_which.return_value = None

        installer = HomebrewInstaller()

        assert installer.is_available() is False

        result = installer.install("any-package", InstallMethod.CASK)
        assert result.status == InstallStatus.FAILED
        assert "not installed" in result.message.lower()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_timeout_handling(
        self,
        mock_run: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test handling of command timeouts."""
        import subprocess

        mock_which.return_value = "/opt/homebrew/bin/brew"

        # First two calls succeed (for cache), third call times out
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas list
            MagicMock(returncode=0, stdout=""),  # casks list
            subprocess.TimeoutExpired(cmd="brew install", timeout=600),  # install times out
        ]

        installer = HomebrewInstaller()
        result = installer.install("slow-package", InstallMethod.CASK)

        assert result.status == InstallStatus.FAILED
        assert "timed out" in result.message.lower()
