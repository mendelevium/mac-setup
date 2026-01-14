"""Tests for UI display functions."""

from io import StringIO
from unittest.mock import patch

from rich.console import Console

from mac_setup.installers.base import InstallResult, InstallStatus
from mac_setup.models import Category, InstalledPackage, InstallMethod, InstallSource, Package
from mac_setup.ui.display import (
    print_banner,
    print_category_table,
    print_error,
    print_info,
    print_install_plan,
    print_installed_packages,
    print_package_table,
    print_status,
    print_success,
    print_summary,
    print_uninstall_plan,
    print_update_plan,
    print_warning,
)


class TestPrintMessages:
    """Tests for print message functions."""

    def test_print_info(self) -> None:
        """Test print_info outputs correctly."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_info("Test message")
        assert "INFO" in output.getvalue()
        assert "Test message" in output.getvalue()

    def test_print_success(self) -> None:
        """Test print_success outputs correctly."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_success("Success message")
        assert "SUCCESS" in output.getvalue()

    def test_print_warning(self) -> None:
        """Test print_warning outputs correctly."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_warning("Warning message")
        assert "WARNING" in output.getvalue()

    def test_print_error(self) -> None:
        """Test print_error outputs correctly."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_error("Error message")
        assert "ERROR" in output.getvalue()


class TestPrintBanner:
    """Tests for print_banner function."""

    def test_print_banner_outputs_version(self) -> None:
        """Test that banner includes version."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_banner()
        result = output.getvalue()
        assert "mac-setup" in result
        assert "Welcome" in result


class TestPrintCategoryTable:
    """Tests for print_category_table function."""

    def test_print_category_table_basic(self) -> None:
        """Test basic category table output."""
        categories = [
            Category(
                id="test",
                name="Test Category",
                description="Test description",
                icon="🧪",
                packages=[
                    Package(
                        id="pkg1", name="Pkg1", description="Desc1",
                        method=InstallMethod.FORMULA
                    ),
                ],
            )
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_category_table(categories)
        result = output.getvalue()
        assert "Test Category" in result
        assert "Categories" in result

    def test_print_category_table_with_selection(self) -> None:
        """Test category table with selected items."""
        categories = [
            Category(
                id="test",
                name="Test Category",
                description="Test description",
                packages=[],
            )
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_category_table(categories, selected={"test"})
        result = output.getvalue()
        assert "✓" in result


class TestPrintPackageTable:
    """Tests for print_package_table function."""

    def test_print_package_table_basic(self) -> None:
        """Test basic package table output."""
        category = Category(
            id="test",
            name="Test Category",
            description="Test description",
            packages=[
                Package(
                    id="pkg1", name="Package 1", description="Description 1",
                    method=InstallMethod.FORMULA
                ),
                Package(
                    id="pkg2", name="Package 2", description="Description 2",
                    method=InstallMethod.CASK, default=True
                ),
            ],
        )
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_package_table(category)
        result = output.getvalue()
        assert "Package 1" in result
        assert "Package 2" in result
        assert "default" in result
        assert "Type" in result
        assert "formula" in result
        assert "cask" in result

    def test_print_package_table_with_installed(self) -> None:
        """Test package table showing installed packages."""
        category = Category(
            id="test",
            name="Test",
            description="Test",
            packages=[
                Package(
                    id="pkg1", name="Package 1", description="Desc",
                    method=InstallMethod.FORMULA
                ),
            ],
        )
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_package_table(category, installed={"pkg1"})
        result = output.getvalue()
        assert "installed" in result


class TestPrintInstalledPackages:
    """Tests for print_installed_packages function."""

    def test_print_empty_list(self) -> None:
        """Test printing empty package list."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_installed_packages([])
        result = output.getvalue()
        assert "no" in result.lower()

    def test_print_packages_with_versions(self) -> None:
        """Test printing packages with version info."""
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP, version="1.0.0"
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_installed_packages(packages, available_versions={"pkg1": "1.1.0"})
        result = output.getvalue()
        assert "Package 1" in result
        assert "1.0.0" in result
        assert "1.1.0" in result

    def test_print_packages_without_version(self) -> None:
        """Test printing packages without version."""
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_installed_packages(packages)
        result = output.getvalue()
        assert "Package 1" in result


class TestPrintInstallPlan:
    """Tests for print_install_plan function."""

    def test_print_install_plan_basic(self) -> None:
        """Test basic install plan output."""
        packages = [
            Package(
                id="pkg1", name="Package 1", description="Desc 1",
                method=InstallMethod.FORMULA
            ),
            Package(
                id="pkg2", name="Package 2", description="Desc 2",
                method=InstallMethod.CASK
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_install_plan(packages)
        result = output.getvalue()
        assert "Package 1" in result
        assert "Package 2" in result
        assert "Total" in result
        assert "2" in result

    def test_print_install_plan_dry_run(self) -> None:
        """Test install plan in dry run mode."""
        packages = [
            Package(id="pkg1", name="Package 1", description="Desc", method=InstallMethod.FORMULA),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_install_plan(packages, dry_run=True)
        result = output.getvalue()
        assert "DRY RUN" in result


class TestPrintUninstallPlan:
    """Tests for print_uninstall_plan function."""

    def test_print_uninstall_plan_standard(self) -> None:
        """Test standard uninstall plan output."""
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_uninstall_plan(packages)
        result = output.getvalue()
        assert "Package 1" in result
        assert "Standard" in result

    def test_print_uninstall_plan_clean(self) -> None:
        """Test clean uninstall plan output."""
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.CASK,
                source=InstallSource.MAC_SETUP
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_uninstall_plan(packages, clean=True)
        result = output.getvalue()
        assert "Clean" in result
        assert "settings" in result.lower()

    def test_print_uninstall_plan_dry_run(self) -> None:
        """Test uninstall plan in dry run mode."""
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_uninstall_plan(packages, dry_run=True)
        result = output.getvalue()
        assert "DRY RUN" in result


class TestPrintUpdatePlan:
    """Tests for print_update_plan function."""

    def test_print_update_plan(self) -> None:
        """Test update plan output."""
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP, version="1.0"
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_update_plan(packages, {"pkg1": "2.0"})
        result = output.getvalue()
        assert "Package 1" in result
        assert "1.0" in result
        assert "2.0" in result

    def test_print_update_plan_dry_run(self) -> None:
        """Test update plan in dry run mode."""
        packages = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_update_plan(packages, {}, dry_run=True)
        result = output.getvalue()
        assert "DRY RUN" in result


class TestPrintSummary:
    """Tests for print_summary function."""

    def test_print_summary_all_success(self) -> None:
        """Test summary with all successful installs."""
        results = [
            InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS),
            InstallResult(package_id="pkg2", status=InstallStatus.SUCCESS),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_summary(results)
        result = output.getvalue()
        assert "2" in result
        assert "successfully" in result

    def test_print_summary_with_failures(self) -> None:
        """Test summary with failed installs."""
        results = [
            InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS),
            InstallResult(package_id="pkg2", status=InstallStatus.FAILED, message="Error"),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_summary(results)
        result = output.getvalue()
        assert "failed" in result.lower()
        assert "pkg2" in result

    def test_print_summary_with_skipped(self) -> None:
        """Test summary with skipped packages."""
        results = [
            InstallResult(package_id="pkg1", status=InstallStatus.SKIPPED),
            InstallResult(package_id="pkg2", status=InstallStatus.ALREADY_INSTALLED),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_summary(results)
        result = output.getvalue()
        assert "skipped" in result.lower() or "already" in result.lower()

    def test_print_summary_with_elapsed_time(self) -> None:
        """Test summary with elapsed time."""
        results = [
            InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_summary(results, elapsed_time=125.5)  # 2m 5s
        result = output.getvalue()
        assert "2m" in result
        assert "5s" in result

    def test_print_summary_short_time(self) -> None:
        """Test summary with short elapsed time."""
        results = [
            InstallResult(package_id="pkg1", status=InstallStatus.SUCCESS),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_summary(results, elapsed_time=45)
        result = output.getvalue()
        assert "45s" in result


class TestPrintStatus:
    """Tests for print_status function."""

    def test_print_status_empty(self) -> None:
        """Test status with no packages."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_status([], [])
        result = output.getvalue()
        assert "No tracked packages" in result

    def test_print_status_with_mac_setup_packages(self) -> None:
        """Test status with mac-setup packages."""
        mac_setup = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_status(mac_setup, [])
        result = output.getvalue()
        assert "mac-setup" in result
        assert "Package 1" in result

    def test_print_status_with_detected_packages(self) -> None:
        """Test status with detected packages."""
        detected = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.CASK,
                source=InstallSource.DETECTED
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_status([], detected)
        result = output.getvalue()
        assert "Detected" in result

    def test_print_status_total_count(self) -> None:
        """Test status shows total count."""
        mac_setup = [
            InstalledPackage(
                id="pkg1", name="Package 1", method=InstallMethod.FORMULA,
                source=InstallSource.MAC_SETUP
            ),
        ]
        detected = [
            InstalledPackage(
                id="pkg2", name="Package 2", method=InstallMethod.CASK,
                source=InstallSource.DETECTED
            ),
        ]
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        with patch("mac_setup.ui.display.console", console):
            print_status(mac_setup, detected)
        result = output.getvalue()
        assert "Total" in result
        assert "2" in result
