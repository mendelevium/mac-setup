"""Package installers for mac-setup."""

from mac_setup.installers.base import Installer, InstallResult
from mac_setup.installers.homebrew import HomebrewInstaller
from mac_setup.installers.mas import MASInstaller
from mac_setup.installers.scanner import ApplicationScanner
from mac_setup.models import InstallMethod

__all__ = [
    "Installer",
    "InstallResult",
    "HomebrewInstaller",
    "MASInstaller",
    "ApplicationScanner",
    "get_installer",
]


def get_installer(method: InstallMethod) -> Installer:
    """Get the appropriate installer for an installation method.

    Args:
        method: The installation method (formula, cask, mas)

    Returns:
        An installer instance for the specified method

    Raises:
        ValueError: If the method is not supported
    """
    if method in (InstallMethod.FORMULA, InstallMethod.CASK):
        return HomebrewInstaller()
    elif method == InstallMethod.MAS:
        return MASInstaller()
    else:
        raise ValueError(f"Unsupported installation method: {method}")
