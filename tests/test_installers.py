"""Tests for package installers (all subprocess calls mocked)."""

from unittest.mock import MagicMock, patch

import pytest

from mac_setup.installers import HomebrewInstaller, MASInstaller, get_installer
from mac_setup.installers.base import InstallResult, InstallStatus
from mac_setup.models import InstallMethod


class TestInstallResult:
    """Tests for InstallResult dataclass."""

    def test_success_property_true_on_success(self) -> None:
        """Test that success property is True for SUCCESS status."""
        result = InstallResult(
            package_id="test",
            status=InstallStatus.SUCCESS,
        )
        assert result.success is True

    def test_success_property_true_on_already_installed(self) -> None:
        """Test that success property is True for ALREADY_INSTALLED status."""
        result = InstallResult(
            package_id="test",
            status=InstallStatus.ALREADY_INSTALLED,
        )
        assert result.success is True

    def test_success_property_false_on_failure(self) -> None:
        """Test that success property is False for FAILED status."""
        result = InstallResult(
            package_id="test",
            status=InstallStatus.FAILED,
        )
        assert result.success is False

    def test_success_property_false_on_skipped(self) -> None:
        """Test that success property is False for SKIPPED status."""
        result = InstallResult(
            package_id="test",
            status=InstallStatus.SKIPPED,
        )
        assert result.success is False


class TestGetInstaller:
    """Tests for get_installer factory function."""

    def test_get_installer_formula(self) -> None:
        """Test getting installer for formula method."""
        installer = get_installer(InstallMethod.FORMULA)
        assert isinstance(installer, HomebrewInstaller)

    def test_get_installer_cask(self) -> None:
        """Test getting installer for cask method."""
        installer = get_installer(InstallMethod.CASK)
        assert isinstance(installer, HomebrewInstaller)

    def test_get_installer_mas(self) -> None:
        """Test getting installer for MAS method."""
        installer = get_installer(InstallMethod.MAS)
        assert isinstance(installer, MASInstaller)


class TestHomebrewInstaller:
    """Tests for HomebrewInstaller."""

    @patch("shutil.which")
    def test_is_available_when_brew_exists(self, mock_which: MagicMock) -> None:
        """Test is_available returns True when brew is found."""
        mock_which.return_value = "/opt/homebrew/bin/brew"
        installer = HomebrewInstaller()
        assert installer.is_available() is True

    @patch("shutil.which")
    def test_is_available_when_brew_missing(self, mock_which: MagicMock) -> None:
        """Test is_available returns False when brew is not found."""
        mock_which.return_value = None
        installer = HomebrewInstaller()
        assert installer.is_available() is False

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_is_installed_formula(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test checking if a formula is installed."""
        mock_which.return_value = "/opt/homebrew/bin/brew"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="git\nripgrep\nfd\n",
        )

        installer = HomebrewInstaller()
        assert installer.is_installed("git", InstallMethod.FORMULA) is True
        assert installer.is_installed("ripgrep", InstallMethod.FORMULA) is True
        assert installer.is_installed("nonexistent", InstallMethod.FORMULA) is False

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_is_installed_cask(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test checking if a cask is installed."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        # First call for formulas, second for casks
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),
            MagicMock(returncode=0, stdout="google-chrome\niterm2\n"),
        ]

        installer = HomebrewInstaller()
        assert installer.is_installed("google-chrome", InstallMethod.CASK) is True
        assert installer.is_installed("iterm2", InstallMethod.CASK) is True
        assert installer.is_installed("nonexistent", InstallMethod.CASK) is False

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_dry_run(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that dry run doesn't actually install."""
        mock_which.return_value = "/opt/homebrew/bin/brew"
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        installer = HomebrewInstaller()
        result = installer.install("test-pkg", InstallMethod.CASK, dry_run=True)

        assert result.status == InstallStatus.SKIPPED
        assert "dry run" in result.message.lower()
        # Verify install command was NOT called
        for call in mock_run.call_args_list:
            args = call[0][0] if call[0] else call[1].get("args", [])
            assert "install" not in args

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_already_installed(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test installing an already installed package."""
        mock_which.return_value = "/opt/homebrew/bin/brew"
        mock_run.return_value = MagicMock(returncode=0, stdout="test-pkg\n")

        installer = HomebrewInstaller()
        result = installer.install("test-pkg", InstallMethod.CASK)

        assert result.status == InstallStatus.ALREADY_INSTALLED

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_success(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test successful installation."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        # Mock calls: check installed, install, then get_version after install
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas (initial check)
            MagicMock(returncode=0, stdout=""),  # casks (initial check)
            MagicMock(returncode=0, stdout=""),  # install
            MagicMock(returncode=0, stdout=""),  # formulas (for get_version)
            MagicMock(returncode=0, stdout="new-pkg"),  # casks (now installed)
            MagicMock(returncode=0, stdout='{"casks":[{"token":"new-pkg","installed":"1.0"}]}'),  # info
        ]

        installer = HomebrewInstaller()
        result = installer.install("new-pkg", InstallMethod.CASK)

        assert result.status == InstallStatus.SUCCESS
        assert result.version == "1.0"

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_failure(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test failed installation."""
        mock_which.return_value = "/opt/homebrew/bin/brew"

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas
            MagicMock(returncode=0, stdout=""),  # casks
            MagicMock(returncode=1, stderr="Error: No formula found"),  # install
        ]

        installer = HomebrewInstaller()
        result = installer.install("bad-pkg", InstallMethod.FORMULA)

        assert result.status == InstallStatus.FAILED
        assert "No formula found" in result.message

    @patch("shutil.which")
    def test_install_homebrew_not_available(self, mock_which: MagicMock) -> None:
        """Test installation when Homebrew is not available."""
        mock_which.return_value = None

        installer = HomebrewInstaller()
        result = installer.install("test-pkg", InstallMethod.CASK)

        assert result.status == InstallStatus.FAILED
        assert "not installed" in result.message.lower()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_uninstall_dry_run(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that dry run uninstall doesn't actually uninstall."""
        mock_which.return_value = "/opt/homebrew/bin/brew"
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # formulas
            MagicMock(returncode=0, stdout="test-pkg\n"),  # casks
        ]

        installer = HomebrewInstaller()
        result = installer.uninstall("test-pkg", InstallMethod.CASK, dry_run=True)

        assert result.status == InstallStatus.SKIPPED
        assert "dry run" in result.message.lower()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_list_installed(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test listing installed packages."""
        mock_which.return_value = "/opt/homebrew/bin/brew"
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="git\nfd\n"),  # formulas
            MagicMock(returncode=0, stdout="chrome\niterm2\n"),  # casks
        ]

        installer = HomebrewInstaller()
        installed = installer.list_installed()

        assert "git" in installed
        assert "fd" in installed
        assert "chrome" in installed
        assert "iterm2" in installed

    def test_get_potential_app_names(self) -> None:
        """Test generating potential app names from cask ID."""
        installer = HomebrewInstaller()
        names = installer._get_potential_app_names("google-chrome")

        assert "google-chrome" in names
        assert "Google Chrome" in names
        assert "GoogleChrome" in names

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_versioned_formula_detection(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that versioned formulas like python@3.12 are detected."""
        mock_which.return_value = "/opt/homebrew/bin/brew"
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="python@3.12\nnode\n"),  # formulas
            MagicMock(returncode=0, stdout=""),  # casks
        ]

        installer = HomebrewInstaller()
        assert installer.is_installed("python@3.12", InstallMethod.FORMULA) is True
        assert installer.is_installed("python", InstallMethod.FORMULA) is True


class TestMASInstaller:
    """Tests for MASInstaller."""

    @patch("shutil.which")
    def test_is_available_when_mas_exists(self, mock_which: MagicMock) -> None:
        """Test is_available returns True when mas is found."""
        mock_which.return_value = "/opt/homebrew/bin/mas"
        installer = MASInstaller()
        assert installer.is_available() is True

    @patch("shutil.which")
    def test_is_available_when_mas_missing(self, mock_which: MagicMock) -> None:
        """Test is_available returns False when mas is not found."""
        mock_which.return_value = None
        installer = MASInstaller()
        assert installer.is_available() is False

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_is_installed(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test checking if a MAS app is installed."""
        mock_which.return_value = "/opt/homebrew/bin/mas"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="937984704 Amphetamine (5.3.1)\n123456789 Another App (1.0)\n",
        )

        installer = MASInstaller()
        assert installer.is_installed("amphetamine", mas_id=937984704) is True
        assert installer.is_installed("other", mas_id=999999999) is False

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_dry_run(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that dry run doesn't actually install."""
        mock_which.return_value = "/opt/homebrew/bin/mas"
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        installer = MASInstaller()
        result = installer.install("test-app", mas_id=123456, dry_run=True)

        assert result.status == InstallStatus.SKIPPED
        assert "dry run" in result.message.lower()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_already_installed(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test installing an already installed app."""
        mock_which.return_value = "/opt/homebrew/bin/mas"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="123456 Test App (1.0)\n",
        )

        installer = MASInstaller()
        result = installer.install("test-app", mas_id=123456)

        assert result.status == InstallStatus.ALREADY_INSTALLED

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_install_success(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test successful installation."""
        mock_which.return_value = "/opt/homebrew/bin/mas"

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),  # list (not installed)
            MagicMock(returncode=0, stdout=""),  # install
        ]

        installer = MASInstaller()
        result = installer.install("new-app", mas_id=123456)

        assert result.status == InstallStatus.SUCCESS

    @patch("shutil.which")
    def test_install_mas_not_available(self, mock_which: MagicMock) -> None:
        """Test installation when mas is not available."""
        mock_which.return_value = None

        installer = MASInstaller()
        result = installer.install("test-app", mas_id=123456)

        assert result.status == InstallStatus.FAILED
        assert "mas-cli" in result.message.lower()

    @patch("shutil.which")
    def test_install_no_mas_id(self, mock_which: MagicMock) -> None:
        """Test installation without mas_id."""
        mock_which.return_value = "/opt/homebrew/bin/mas"

        installer = MASInstaller()
        result = installer.install("test-app", mas_id=None)

        assert result.status == InstallStatus.FAILED
        assert "no mac app store id" in result.message.lower()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_uninstall_not_supported(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test that uninstall returns appropriate message."""
        mock_which.return_value = "/opt/homebrew/bin/mas"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="123456 Test App (1.0)\n",
        )

        installer = MASInstaller()
        result = installer.uninstall("test-app", mas_id=123456)

        assert result.status == InstallStatus.FAILED
        assert "manually" in result.message.lower()

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_list_installed(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test listing installed MAS apps."""
        mock_which.return_value = "/opt/homebrew/bin/mas"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="937984704 Amphetamine (5.3.1)\n123456789 Test App (1.0)\n",
        )

        installer = MASInstaller()
        installed = installer.list_installed()

        assert "Amphetamine" in installed
        assert "Test App" in installed

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_list_installed_ids(
        self, mock_run: MagicMock, mock_which: MagicMock
    ) -> None:
        """Test listing installed MAS app IDs."""
        mock_which.return_value = "/opt/homebrew/bin/mas"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="937984704 Amphetamine (5.3.1)\n123456789 Test App (1.0)\n",
        )

        installer = MASInstaller()
        installed_ids = installer.list_installed_ids()

        assert 937984704 in installed_ids
        assert 123456789 in installed_ids
