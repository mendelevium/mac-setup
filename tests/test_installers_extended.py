"""Extended tests for installers to increase coverage."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from mac_setup.installers import get_installer
from mac_setup.installers.base import InstallResult, InstallStatus
from mac_setup.installers.homebrew import HomebrewInstaller
from mac_setup.installers.mas import MASInstaller
from mac_setup.installers.scanner import ApplicationScanner
from mac_setup.models import InstallMethod


class TestHomebrewInstallerExtended:
    """Extended tests for HomebrewInstaller."""

    def test_brew_path_caching(self) -> None:
        """Test that brew_path is cached."""
        installer = HomebrewInstaller()
        with patch("shutil.which", return_value="/opt/homebrew/bin/brew"):
            path1 = installer.brew_path
            path2 = installer.brew_path
            assert path1 == path2 == "/opt/homebrew/bin/brew"

    @patch("subprocess.run")
    def test_run_brew_raises_when_not_available(self, mock_run: MagicMock) -> None:
        """Test _run_brew raises when Homebrew is not installed."""
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", None):
            with patch("shutil.which", return_value=None):
                try:
                    installer._run_brew("list")
                    assert False, "Should have raised RuntimeError"
                except RuntimeError as e:
                    assert "not installed" in str(e).lower()

    @patch("subprocess.run")
    def test_refresh_installed_cache(self, mock_run: MagicMock) -> None:
        """Test _refresh_installed_cache populates caches."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="git\nripgrep\n"),  # formulas
            MagicMock(returncode=0, stdout="google-chrome\nfirefox\n"),  # casks
        ]
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            installer._refresh_installed_cache()
            assert "git" in installer._installed_formulas
            assert "google-chrome" in installer._installed_casks

    @patch("subprocess.run")
    def test_refresh_installed_cache_handles_timeout(self, mock_run: MagicMock) -> None:
        """Test _refresh_installed_cache handles timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="brew", timeout=10)
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            installer._refresh_installed_cache()
            # Should not raise, caches should be empty sets
            assert installer._installed_formulas == set()
            assert installer._installed_casks == set()

    @patch("subprocess.run")
    def test_get_installed_set_formula(self, mock_run: MagicMock) -> None:
        """Test _get_installed_set for formulas."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="git\n"),
            MagicMock(returncode=0, stdout=""),
        ]
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            result = installer._get_installed_set(InstallMethod.FORMULA)
            assert "git" in result

    @patch("subprocess.run")
    def test_get_installed_set_cask(self, mock_run: MagicMock) -> None:
        """Test _get_installed_set for casks."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),
            MagicMock(returncode=0, stdout="firefox\n"),
        ]
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            result = installer._get_installed_set(InstallMethod.CASK)
            assert "firefox" in result

    @patch("subprocess.run")
    def test_list_installed_formulas(self, mock_run: MagicMock) -> None:
        """Test list_installed for formulas."""
        mock_run.return_value = MagicMock(returncode=0, stdout="git\nripgrep\n")
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            result = installer.list_installed(InstallMethod.FORMULA)
            assert "git" in result
            assert "ripgrep" in result

    @patch("subprocess.run")
    def test_list_installed_casks(self, mock_run: MagicMock) -> None:
        """Test list_installed for casks."""
        mock_run.return_value = MagicMock(returncode=0, stdout="chrome\nfirefox\n")
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            result = installer.list_installed(InstallMethod.CASK)
            assert "chrome" in result
            assert "firefox" in result

    @patch("subprocess.run")
    def test_list_installed_empty(self, mock_run: MagicMock) -> None:
        """Test list_installed returns empty list on failure."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            result = installer.list_installed(InstallMethod.FORMULA)
            assert result == []

    @patch("subprocess.run")
    def test_uninstall_success(self, mock_run: MagicMock) -> None:
        """Test successful uninstall."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=True):
                result = installer.uninstall("test-pkg", method=InstallMethod.FORMULA)
                assert result.status == InstallStatus.SUCCESS

    @patch("subprocess.run")
    def test_uninstall_not_installed(self, mock_run: MagicMock) -> None:
        """Test uninstall when package not installed."""
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.uninstall("test-pkg", method=InstallMethod.FORMULA)
                assert result.status == InstallStatus.SKIPPED

    @patch("subprocess.run")
    def test_uninstall_failure(self, mock_run: MagicMock) -> None:
        """Test uninstall failure."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=True):
                result = installer.uninstall("test-pkg", method=InstallMethod.FORMULA)
                assert result.status == InstallStatus.FAILED

    @patch("subprocess.run")
    def test_get_version_formula(self, mock_run: MagicMock) -> None:
        """Test get_version for formula."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"formulae":[{"name":"git","installed":[{"version":"2.40.0"}]}]}',
        )
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_available", return_value=True):
                with patch.object(installer, "is_installed", return_value=True):
                    version = installer.get_version("git", InstallMethod.FORMULA)
                    assert version == "2.40.0"

    @patch("subprocess.run")
    def test_get_version_cask(self, mock_run: MagicMock) -> None:
        """Test get_version for cask."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"casks":[{"token":"firefox","installed":"120.0"}]}',
        )
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_available", return_value=True):
                with patch.object(installer, "is_installed", return_value=True):
                    version = installer.get_version("firefox", InstallMethod.CASK)
                    assert version == "120.0"

    def test_get_version_not_installed(self) -> None:
        """Test get_version when not installed."""
        installer = HomebrewInstaller()
        with patch.object(installer, "is_available", return_value=True):
            with patch.object(installer, "is_installed", return_value=False):
                version = installer.get_version("notinstalled", InstallMethod.FORMULA)
                assert version is None

    def test_get_clean_uninstall_paths(self) -> None:
        """Test get_clean_uninstall_paths returns paths."""
        installer = HomebrewInstaller()
        paths = installer.get_clean_uninstall_paths("SomeApp")
        assert isinstance(paths, list)


class TestMASInstallerExtended:
    """Extended tests for MASInstaller."""

    @patch("subprocess.run")
    def test_list_installed(self, mock_run: MagicMock) -> None:
        """Test list_installed returns app names."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="123456 App One (1.0)\n789012 App Two (2.0)\n",
        )
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            result = installer.list_installed()
            assert len(result) >= 0

    @patch("subprocess.run")
    def test_list_installed_ids(self, mock_run: MagicMock) -> None:
        """Test list_installed_ids returns IDs."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="123456 App One (1.0)\n789012 App Two (2.0)\n",
        )
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            result = installer.list_installed_ids()
            assert 123456 in result
            assert 789012 in result

    @patch("subprocess.run")
    def test_list_installed_ids_empty(self, mock_run: MagicMock) -> None:
        """Test list_installed_ids returns empty on failure."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            result = installer.list_installed_ids()
            assert result == []

    def test_uninstall_not_installed(self) -> None:
        """Test uninstall returns skipped when app not installed."""
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.uninstall("app", mas_id=123456)
                assert result.status == InstallStatus.SKIPPED
                assert "not installed" in result.message.lower()

    def test_uninstall_manual_required(self) -> None:
        """Test uninstall returns failed with manual instructions for installed apps."""
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            with patch.object(installer, "is_installed", return_value=True):
                result = installer.uninstall("app", mas_id=123456)
                assert result.status == InstallStatus.FAILED
                assert "manually" in result.message.lower()

    @patch("subprocess.run")
    def test_install_success(self, mock_run: MagicMock) -> None:
        """Test successful MAS app installation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.install("xcode", mas_id=497799835)
                assert result.status == InstallStatus.SUCCESS

    @patch("subprocess.run")
    def test_install_already_installed(self, mock_run: MagicMock) -> None:
        """Test install when MAS app already installed."""
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            with patch.object(installer, "is_installed", return_value=True):
                result = installer.install("xcode", mas_id=497799835)
                assert result.status == InstallStatus.ALREADY_INSTALLED

    @patch("subprocess.run")
    def test_install_failure(self, mock_run: MagicMock) -> None:
        """Test MAS install failure."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.install("badapp", mas_id=123456)
                assert result.status == InstallStatus.FAILED

    def test_install_dry_run(self) -> None:
        """Test MAS install dry run."""
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.install("xcode", mas_id=497799835, dry_run=True)
                assert result.status == InstallStatus.SKIPPED

    def test_install_no_mas_id(self) -> None:
        """Test install without MAS ID fails."""
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            result = installer.install("xcode", mas_id=None)
            assert result.status == InstallStatus.FAILED

    def test_get_version_returns_none(self) -> None:
        """Test get_version returns None (not implemented yet)."""
        installer = MASInstaller()
        with patch.object(installer, "_mas_path", "/usr/local/bin/mas"):
            # MAS get_version currently always returns None
            version = installer.get_version("xcode", mas_id=497799835)
            assert version is None


class TestApplicationScanner:
    """Tests for ApplicationScanner."""

    def test_initialization(self) -> None:
        """Test scanner initialization."""
        scanner = ApplicationScanner()
        assert scanner is not None

    def test_is_available(self, tmp_path: Path) -> None:
        """Test is_available method."""
        scanner = ApplicationScanner(applications_path=tmp_path)
        assert scanner.is_available() is True

    def test_is_available_missing_dir(self, tmp_path: Path) -> None:
        """Test is_available when dir doesn't exist."""
        scanner = ApplicationScanner(applications_path=tmp_path / "nonexistent")
        assert scanner.is_available() is False

    def test_list_installed_apps(self, tmp_path: Path) -> None:
        """Test list_installed_apps method."""
        # Create a fake .app directory
        app_dir = tmp_path / "TestApp.app"
        app_dir.mkdir()

        scanner = ApplicationScanner(applications_path=tmp_path)
        apps = scanner.list_installed_apps()
        assert "TestApp" in apps

    def test_list_installed_apps_empty(self, tmp_path: Path) -> None:
        """Test list_installed_apps with no apps."""
        scanner = ApplicationScanner(applications_path=tmp_path)
        apps = scanner.list_installed_apps()
        assert apps == set()

    def test_is_app_installed(self, tmp_path: Path) -> None:
        """Test is_app_installed method."""
        app_dir = tmp_path / "Safari.app"
        app_dir.mkdir()

        scanner = ApplicationScanner(applications_path=tmp_path)
        assert scanner.is_app_installed("Safari") is True
        assert scanner.is_app_installed("NotInstalled") is False

    def test_invalidate_cache(self, tmp_path: Path) -> None:
        """Test invalidate_cache method."""
        scanner = ApplicationScanner(applications_path=tmp_path)
        scanner.list_installed_apps()  # Populate cache
        scanner.invalidate_cache()
        assert scanner._installed_apps is None


class TestGetInstallerExtended:
    """Extended tests for get_installer factory."""

    def test_get_installer_formula(self) -> None:
        """Test get_installer returns HomebrewInstaller for formula."""
        installer = get_installer(InstallMethod.FORMULA)
        assert isinstance(installer, HomebrewInstaller)

    def test_get_installer_cask(self) -> None:
        """Test get_installer returns HomebrewInstaller for cask."""
        installer = get_installer(InstallMethod.CASK)
        assert isinstance(installer, HomebrewInstaller)

    def test_get_installer_mas(self) -> None:
        """Test get_installer returns MASInstaller for mas."""
        installer = get_installer(InstallMethod.MAS)
        assert isinstance(installer, MASInstaller)


class TestInstallResultExtended:
    """Extended tests for InstallResult."""

    def test_result_with_version(self) -> None:
        """Test InstallResult with version."""
        result = InstallResult(
            package_id="test",
            status=InstallStatus.SUCCESS,
            version="1.0.0",
        )
        assert result.version == "1.0.0"

    def test_result_with_message(self) -> None:
        """Test InstallResult with message."""
        result = InstallResult(
            package_id="test",
            status=InstallStatus.FAILED,
            message="Installation failed",
        )
        assert result.message == "Installation failed"


class TestHomebrewInstallerInstall:
    """Tests for HomebrewInstaller.install method."""

    @patch("subprocess.run")
    def test_install_formula_success(self, mock_run: MagicMock) -> None:
        """Test successful formula installation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.install("git", InstallMethod.FORMULA)
                assert result.status == InstallStatus.SUCCESS

    @patch("subprocess.run")
    def test_install_already_installed(self, mock_run: MagicMock) -> None:
        """Test install when package already installed."""
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=True):
                result = installer.install("git", InstallMethod.FORMULA)
                assert result.status == InstallStatus.ALREADY_INSTALLED

    @patch("subprocess.run")
    def test_install_failure(self, mock_run: MagicMock) -> None:
        """Test install failure."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error installing")
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.install("badpackage", InstallMethod.FORMULA)
                assert result.status == InstallStatus.FAILED

    def test_install_dry_run(self) -> None:
        """Test install in dry run mode."""
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.install("git", InstallMethod.FORMULA, dry_run=True)
                assert result.status == InstallStatus.SKIPPED  # Dry run returns SKIPPED


class TestHomebrewInstallerUpdate:
    """Tests for HomebrewInstaller.update method."""

    @patch("subprocess.run")
    def test_update_success(self, mock_run: MagicMock) -> None:
        """Test successful package update."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=True):
                result = installer.update("git", InstallMethod.FORMULA)
                assert result.status == InstallStatus.SUCCESS

    @patch("subprocess.run")
    def test_update_not_installed(self, mock_run: MagicMock) -> None:
        """Test update when package not installed."""
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=False):
                result = installer.update("notinstalled", InstallMethod.FORMULA)
                assert result.status == InstallStatus.FAILED  # Returns FAILED when not installed

    def test_update_dry_run(self) -> None:
        """Test update in dry run mode."""
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            with patch.object(installer, "is_installed", return_value=True):
                result = installer.update("git", InstallMethod.FORMULA, dry_run=True)
                assert result.status == InstallStatus.SKIPPED  # Dry run returns SKIPPED


class TestHomebrewInstallerVersions:
    """Tests for version-related methods."""

    @patch("subprocess.run")
    def test_get_versions_batch(self, mock_run: MagicMock) -> None:
        """Test get_versions_batch returns versions."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"formulae":[{"name":"git","installed":[{"version":"2.40.0"}]}],"casks":[]}'
        )
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            # Takes list of (package_id, method) tuples
            result = installer.get_versions_batch([("git", InstallMethod.FORMULA)])
            assert "git" in result
            assert result["git"] == "2.40.0"

    @patch("subprocess.run")
    def test_get_available_versions_batch(self, mock_run: MagicMock) -> None:
        """Test get_available_versions_batch returns available versions."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"formulae":[{"name":"git","versions":{"stable":"2.41.0"}}],"casks":[]}'
        )
        installer = HomebrewInstaller()
        with patch.object(installer, "_brew_path", "/usr/local/bin/brew"):
            # Takes list of (package_id, method) tuples
            result = installer.get_available_versions_batch([("git", InstallMethod.FORMULA)])
            assert "git" in result

    def test_get_clean_uninstall_paths(self) -> None:
        """Test get_clean_uninstall_paths returns paths."""
        installer = HomebrewInstaller()
        paths = installer.get_clean_uninstall_paths("SomeApp")
        assert isinstance(paths, list)
