"""Tests for UI progress tracking."""

from io import StringIO
from unittest.mock import patch

from rich.console import Console

from mac_setup.installers.base import InstallResult, InstallStatus
from mac_setup.ui.progress import (
    InstallProgress,
    UninstallProgress,
    UpdateProgress,
    install_progress,
    print_spinner,
    uninstall_progress,
    update_progress,
)


class TestInstallProgress:
    """Tests for InstallProgress class."""

    def test_initialization(self) -> None:
        """Test progress tracker initialization."""
        progress = InstallProgress(total_packages=5)
        assert progress.total == 5
        assert progress.current == 0
        assert progress.completed == []
        assert progress.current_package is None

    def test_update_sets_current_package(self) -> None:
        """Test update method sets current package."""
        progress = InstallProgress(total_packages=3)
        progress.start()
        progress.update("test-package")
        assert progress.current_package == "test-package"
        progress.stop()

    def test_complete_package_increments_counter(self) -> None:
        """Test complete_package increments counter."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = InstallProgress(total_packages=3)
            progress.start()
            result = InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS)
            progress.complete_package(result)
            assert progress.current == 1
            assert len(progress.completed) == 1
            progress.stop()

    def test_success_count(self) -> None:
        """Test success_count property."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = InstallProgress(total_packages=3)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS)
            )
            progress.complete_package(
                InstallResult(package_id="pkg2", status=InstallStatus.FAILED)
            )
            progress.complete_package(
                InstallResult(package_id="pkg3", status=InstallStatus.SUCCESS)
            )
            assert progress.success_count == 2
            progress.stop()

    def test_failed_count(self) -> None:
        """Test failed_count property."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = InstallProgress(total_packages=2)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS)
            )
            progress.complete_package(
                InstallResult(package_id="pkg2", status=InstallStatus.FAILED)
            )
            assert progress.failed_count == 1
            progress.stop()

    def test_skipped_count(self) -> None:
        """Test skipped_count property."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = InstallProgress(total_packages=3)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SKIPPED)
            )
            progress.complete_package(
                InstallResult(package_id="pkg2", status=InstallStatus.ALREADY_INSTALLED)
            )
            progress.complete_package(
                InstallResult(package_id="pkg3", status=InstallStatus.SUCCESS)
            )
            assert progress.skipped_count == 2
            progress.stop()

    def test_complete_package_prints_status(self) -> None:
        """Test complete_package prints status for each type."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = InstallProgress(total_packages=4)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS)
            )
            progress.complete_package(
                InstallResult(package_id="pkg2", status=InstallStatus.ALREADY_INSTALLED)
            )
            progress.complete_package(
                InstallResult(package_id="pkg3", status=InstallStatus.SKIPPED)
            )
            progress.complete_package(
                InstallResult(package_id="pkg4", status=InstallStatus.FAILED, message="Error")
            )
            progress.stop()
        result = output.getvalue()
        assert "pkg1" in result
        assert "already installed" in result
        assert "skipped" in result
        assert "Error" in result


class TestInstallProgressContextManager:
    """Tests for install_progress context manager."""

    def test_context_manager_starts_and_stops(self) -> None:
        """Test context manager handles start/stop."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            with install_progress(3) as progress:
                assert progress.total == 3
                progress.update("test")

    def test_context_manager_stops_on_exception(self) -> None:
        """Test context manager stops progress on exception."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            try:
                with install_progress(3) as progress:
                    progress.update("test")
                    raise ValueError("Test error")
            except ValueError:
                pass
            # Progress should be stopped even after exception


class TestUninstallProgress:
    """Tests for UninstallProgress class."""

    def test_initialization(self) -> None:
        """Test uninstall progress initialization."""
        progress = UninstallProgress(total_packages=5)
        assert progress.total == 5
        assert progress.current == 0

    def test_update_method(self) -> None:
        """Test update method."""
        progress = UninstallProgress(total_packages=3)
        progress.start()
        progress.update("test-package")
        progress.stop()

    def test_complete_package(self) -> None:
        """Test complete_package method."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = UninstallProgress(total_packages=3)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS)
            )
            assert progress.current == 1
            progress.stop()

    def test_complete_package_with_cleaned(self) -> None:
        """Test complete_package with cleaned flag."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = UninstallProgress(total_packages=1)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS),
                cleaned=True
            )
            progress.stop()
        result = output.getvalue()
        assert "cleaned" in result

    def test_complete_package_prints_status(self) -> None:
        """Test complete_package prints status for each type."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = UninstallProgress(total_packages=3)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS)
            )
            progress.complete_package(
                InstallResult(package_id="pkg2", status=InstallStatus.SKIPPED)
            )
            progress.complete_package(
                InstallResult(package_id="pkg3", status=InstallStatus.FAILED, message="Error")
            )
            progress.stop()
        result = output.getvalue()
        assert "pkg1" in result
        assert "skipped" in result


class TestUninstallProgressContextManager:
    """Tests for uninstall_progress context manager."""

    def test_context_manager(self) -> None:
        """Test context manager handles start/stop."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            with uninstall_progress(2) as progress:
                assert progress.total == 2


class TestUpdateProgress:
    """Tests for UpdateProgress class."""

    def test_initialization(self) -> None:
        """Test update progress initialization."""
        progress = UpdateProgress(total_packages=5)
        assert progress.total == 5
        assert progress.current == 0

    def test_update_method(self) -> None:
        """Test update method."""
        progress = UpdateProgress(total_packages=3)
        progress.start()
        progress.update("test-package")
        progress.stop()

    def test_complete_package(self) -> None:
        """Test complete_package method."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = UpdateProgress(total_packages=3)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS, version="2.0")
            )
            assert progress.current == 1
            progress.stop()
        result = output.getvalue()
        assert "2.0" in result

    def test_complete_package_prints_status(self) -> None:
        """Test complete_package prints status for each type."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            progress = UpdateProgress(total_packages=4)
            progress.start()
            progress.complete_package(
                InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS)
            )
            progress.complete_package(
                InstallResult(package_id="pkg2", status=InstallStatus.ALREADY_INSTALLED)
            )
            progress.complete_package(
                InstallResult(package_id="pkg3", status=InstallStatus.SKIPPED)
            )
            progress.complete_package(
                InstallResult(package_id="pkg4", status=InstallStatus.FAILED, message="Error")
            )
            progress.stop()
        result = output.getvalue()
        assert "pkg1" in result
        assert "up to date" in result
        assert "skipped" in result


class TestUpdateProgressContextManager:
    """Tests for update_progress context manager."""

    def test_context_manager(self) -> None:
        """Test context manager handles start/stop."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            with update_progress(2) as progress:
                assert progress.total == 2


class TestPrintSpinner:
    """Tests for print_spinner function."""

    def test_print_spinner(self) -> None:
        """Test print_spinner displays message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.progress.console", console):
            print_spinner("Loading...")
