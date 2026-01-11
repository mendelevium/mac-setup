"""Base installer interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class InstallStatus(str, Enum):
    """Status of an installation operation."""

    SUCCESS = "success"
    ALREADY_INSTALLED = "already_installed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class InstallResult:
    """Result of an installation operation."""

    package_id: str
    status: InstallStatus
    message: str = ""
    version: str | None = None

    @property
    def success(self) -> bool:
        """Check if installation was successful (including already installed)."""
        return self.status in (InstallStatus.SUCCESS, InstallStatus.ALREADY_INSTALLED)


class Installer(ABC):
    """Abstract base class for package installers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this installer is available on the system.

        Returns:
            True if the installer can be used, False otherwise
        """
        pass

    @abstractmethod
    def is_installed(self, package_id: str) -> bool:
        """Check if a package is already installed.

        Args:
            package_id: The package identifier

        Returns:
            True if installed, False otherwise
        """
        pass

    @abstractmethod
    def install(self, package_id: str, dry_run: bool = False) -> InstallResult:
        """Install a package.

        Args:
            package_id: The package identifier
            dry_run: If True, don't actually install

        Returns:
            InstallResult with the outcome
        """
        pass

    @abstractmethod
    def uninstall(self, package_id: str, dry_run: bool = False) -> InstallResult:
        """Uninstall a package.

        Args:
            package_id: The package identifier
            dry_run: If True, don't actually uninstall

        Returns:
            InstallResult with the outcome
        """
        pass

    @abstractmethod
    def list_installed(self) -> list[str]:
        """List all installed packages managed by this installer.

        Returns:
            List of package identifiers
        """
        pass

    def get_version(self, package_id: str) -> str | None:
        """Get the installed version of a package.

        Args:
            package_id: The package identifier

        Returns:
            Version string if available, None otherwise
        """
        return None
