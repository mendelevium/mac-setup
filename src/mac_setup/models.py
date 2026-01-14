"""Pydantic models for mac-setup."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class InstallMethod(str, Enum):
    """Installation method for a package."""

    FORMULA = "formula"  # Homebrew formula (CLI tools)
    CASK = "cask"  # Homebrew cask (GUI apps)


class Package(BaseModel):
    """A software package that can be installed."""

    id: str = Field(..., description="Homebrew formula/cask name or identifier")
    name: str = Field(..., description="Human-readable display name")
    description: str = Field(..., description="One-line description")
    method: InstallMethod = Field(default=InstallMethod.CASK, description="Installation method")
    app_name: str | None = Field(
        default=None, description="App name in /Applications (e.g., 'Visual Studio Code')"
    )
    default: bool = Field(default=False, description="Whether selected by default in UI")
    requires: list[str] = Field(default_factory=list, description="Package dependencies")


class Category(BaseModel):
    """A category of related packages."""

    id: str = Field(..., description="Category identifier (e.g., 'browsers')")
    name: str = Field(..., description="Display name (e.g., 'Browsers')")
    description: str = Field(..., description="Category description")
    icon: str = Field(default="", description="Emoji icon for display")
    packages: list[Package] = Field(default_factory=list, description="Packages in this category")

    def get_package(self, package_id: str) -> Package | None:
        """Get a package by ID from this category."""
        return next((pkg for pkg in self.packages if pkg.id == package_id), None)

    def get_default_packages(self) -> list[Package]:
        """Get packages marked as default in this category."""
        return [pkg for pkg in self.packages if pkg.default]


class Preset(BaseModel):
    """A saved configuration of selected packages."""

    name: str = Field(..., description="Preset name")
    description: str | None = Field(default=None, description="Preset description")
    version: int = Field(default=1, description="Schema version")
    created: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description="Creation date",
    )
    author: str | None = Field(default=None, description="Preset author")
    packages: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Selected packages by category ID",
    )

    def get_all_package_ids(self) -> list[str]:
        """Get flat list of all package IDs in this preset."""
        all_ids: list[str] = []
        for package_ids in self.packages.values():
            all_ids.extend(package_ids)
        return all_ids

    def package_count(self) -> int:
        """Get total number of packages in this preset."""
        return sum(len(ids) for ids in self.packages.values())


class InstallSource(str, Enum):
    """Source of package installation."""

    MAC_SETUP = "mac-setup"  # Installed via mac-setup
    DETECTED = "detected"  # Found on system, installed externally


class InstalledPackage(BaseModel):
    """Record of an installed package."""

    id: str = Field(..., description="Package identifier")
    name: str = Field(..., description="Package display name")
    method: InstallMethod = Field(..., description="How it was installed")
    source: InstallSource = Field(..., description="Installation source")
    installed_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Installation timestamp",
    )
    version: str | None = Field(default=None, description="Installed version")


class AppState(BaseModel):
    """Application state tracking installed packages."""

    version: int = Field(default=1, description="State schema version")
    packages: list[InstalledPackage] = Field(
        default_factory=list,
        description="List of installed packages",
    )

    def get_package(self, package_id: str) -> InstalledPackage | None:
        """Get an installed package by ID."""
        return next((pkg for pkg in self.packages if pkg.id == package_id), None)

    def add_package(self, package: InstalledPackage) -> None:
        """Add or update an installed package."""
        # Remove existing entry if present
        self.packages = [p for p in self.packages if p.id != package.id]
        self.packages.append(package)

    def remove_package(self, package_id: str) -> bool:
        """Remove a package from state. Returns True if found and removed."""
        original_len = len(self.packages)
        self.packages = [p for p in self.packages if p.id != package_id]
        return len(self.packages) < original_len

    def get_mac_setup_packages(self) -> list[InstalledPackage]:
        """Get packages installed via mac-setup."""
        return [p for p in self.packages if p.source == InstallSource.MAC_SETUP]

    def get_detected_packages(self) -> list[InstalledPackage]:
        """Get packages detected on system (not installed via mac-setup)."""
        return [p for p in self.packages if p.source == InstallSource.DETECTED]
