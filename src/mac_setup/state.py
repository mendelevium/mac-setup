"""State management for tracking installed packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from mac_setup.config import STATE_FILE, ensure_directories
from mac_setup.models import (
    AppState,
    InstallMethod,
    InstalledPackage,
    InstallSource,
    Package,
)

if TYPE_CHECKING:
    from mac_setup.installers.homebrew import HomebrewInstaller
    from mac_setup.installers.scanner import ApplicationScanner


class StateManager:
    """Manages the application state file."""

    def __init__(self, state_file: Path | None = None) -> None:
        """Initialize the state manager.

        Args:
            state_file: Path to state file. Defaults to config.STATE_FILE.
        """
        self.state_file = state_file or STATE_FILE
        self._state: AppState | None = None

    @property
    def state(self) -> AppState:
        """Get the current application state, loading from file if needed."""
        if self._state is None:
            self._state = self.load()
        return self._state

    def load(self) -> AppState:
        """Load state from file.

        Returns:
            AppState instance (empty state if file doesn't exist)
        """
        if not self.state_file.exists():
            return AppState()

        try:
            data = json.loads(self.state_file.read_text())
            return AppState.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            # Corrupt state file - start fresh
            return AppState()

    def save(self) -> None:
        """Save current state to file."""
        ensure_directories()
        self.state_file.write_text(
            self.state.model_dump_json(indent=2)
        )

    def reload(self) -> AppState:
        """Force reload state from file."""
        self._state = self.load()
        return self._state

    def add_installed_package(
        self,
        package: Package,
        source: InstallSource = InstallSource.MAC_SETUP,
        version: str | None = None,
    ) -> None:
        """Record a package as installed.

        Args:
            package: The package that was installed
            source: Whether it was installed by mac-setup or detected
            version: Optional version string
        """
        installed = InstalledPackage(
            id=package.id,
            name=package.name,
            method=package.method,
            source=source,
            version=version,
        )
        self.state.add_package(installed)
        self.save()

    def remove_installed_package(self, package_id: str) -> bool:
        """Remove a package from the installed list.

        Args:
            package_id: The package identifier

        Returns:
            True if package was found and removed, False otherwise
        """
        removed = self.state.remove_package(package_id)
        if removed:
            self.save()
        return removed

    def is_tracked(self, package_id: str) -> bool:
        """Check if a package is tracked in state.

        Args:
            package_id: The package identifier

        Returns:
            True if package is in state
        """
        return self.state.get_package(package_id) is not None

    def get_installed_package(self, package_id: str) -> InstalledPackage | None:
        """Get an installed package by ID.

        Args:
            package_id: The package identifier

        Returns:
            InstalledPackage if found, None otherwise
        """
        return self.state.get_package(package_id)

    def get_mac_setup_packages(self) -> list[InstalledPackage]:
        """Get packages installed via mac-setup."""
        return self.state.get_mac_setup_packages()

    def get_detected_packages(self) -> list[InstalledPackage]:
        """Get packages detected on system (not installed via mac-setup)."""
        return self.state.get_detected_packages()

    def get_all_installed(self) -> list[InstalledPackage]:
        """Get all installed packages."""
        return self.state.packages.copy()

    def clear(self) -> None:
        """Clear all state."""
        self._state = AppState()
        self.save()


def detect_installed_packages(
    catalog_packages: list[Package],
    homebrew_installed: list[str],
    mas_installed: list[int],
    homebrew: HomebrewInstaller | None = None,
    scanner: ApplicationScanner | None = None,
) -> list[InstalledPackage]:
    """Detect which catalog packages are installed on the system.

    Args:
        catalog_packages: List of packages from the catalog
        homebrew_installed: List of installed Homebrew package IDs
        mas_installed: List of installed Mac App Store app IDs
        homebrew: Optional HomebrewInstaller for fetching versions
        scanner: Optional ApplicationScanner for detecting /Applications apps

    Returns:
        List of InstalledPackage for packages found on the system
    """
    installed: list[InstalledPackage] = []
    homebrew_set = set(homebrew_installed)

    # Get installed apps from /Applications if scanner provided
    installed_apps = scanner.list_installed_apps() if scanner else set()

    for pkg in catalog_packages:
        is_installed = False

        if pkg.method == InstallMethod.MAS:
            if pkg.mas_id and pkg.mas_id in mas_installed:
                is_installed = True
        else:
            # Homebrew formula or cask
            if pkg.id in homebrew_set:
                is_installed = True
            # Check versioned formulas (e.g., python@3.12 -> python)
            elif "@" in pkg.id and pkg.id.split("@")[0] in homebrew_set:
                is_installed = True
            # Check /Applications folder for casks with app_name
            elif pkg.app_name and pkg.app_name in installed_apps:
                is_installed = True

        if is_installed:
            installed.append(
                InstalledPackage(
                    id=pkg.id,
                    name=pkg.name,
                    method=pkg.method,
                    source=InstallSource.DETECTED,
                )
            )

    # Batch fetch versions for Homebrew packages if installer provided
    if homebrew and installed:
        homebrew_packages = [
            (inst_pkg.id, inst_pkg.method)
            for inst_pkg in installed
            if inst_pkg.method in (InstallMethod.FORMULA, InstallMethod.CASK)
        ]
        if homebrew_packages:
            versions = homebrew.get_versions_batch(homebrew_packages)
            for inst_pkg in installed:
                if inst_pkg.id in versions:
                    inst_pkg.version = versions[inst_pkg.id]

    return installed


def sync_detected_packages(
    state_manager: StateManager,
    catalog_packages: list[Package],
    homebrew_installed: list[str],
    mas_installed: list[int],
    homebrew: HomebrewInstaller | None = None,
    scanner: ApplicationScanner | None = None,
) -> list[InstalledPackage]:
    """Sync state with actually installed packages.

    This updates the state to reflect packages that are installed on the system
    but not tracked by mac-setup (detected packages). It also removes stale
    detected packages that are no longer installed.

    Args:
        state_manager: The state manager instance
        catalog_packages: List of packages from the catalog
        homebrew_installed: List of installed Homebrew package IDs
        mas_installed: List of installed Mac App Store app IDs
        homebrew: Optional HomebrewInstaller for fetching versions
        scanner: Optional ApplicationScanner for detecting /Applications apps

    Returns:
        List of newly detected packages
    """
    detected = detect_installed_packages(
        catalog_packages, homebrew_installed, mas_installed, homebrew, scanner
    )
    detected_ids = {pkg.id for pkg in detected}
    detected_map = {pkg.id: pkg for pkg in detected}

    newly_detected: list[InstalledPackage] = []
    state_changed = False

    # Remove stale detected packages that are no longer installed
    for existing_pkg in state_manager.get_detected_packages():
        if existing_pkg.id not in detected_ids:
            state_manager.remove_installed_package(existing_pkg.id)
            state_changed = True

    # Add new detected packages and update existing ones
    for pkg in detected:
        existing = state_manager.get_installed_package(pkg.id)
        if existing is None:
            # New package detected - add as detected
            state_manager.state.add_package(pkg)
            newly_detected.append(pkg)
            state_changed = True
        elif existing.source == InstallSource.DETECTED:
            # Update version if it changed
            if existing.version != pkg.version:
                existing.version = pkg.version
                state_changed = True
        # If source is MAC_SETUP, don't change it

    if state_changed:
        state_manager.save()

    return newly_detected
