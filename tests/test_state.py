"""Tests for state management."""

from pathlib import Path

from mac_setup.models import (
    InstallMethod,
    InstallSource,
    Package,
)
from mac_setup.state import (
    StateManager,
    detect_installed_packages,
    sync_detected_packages,
)


class TestStateManager:
    """Tests for StateManager class."""

    def test_load_empty_state(self, tmp_path: Path) -> None:
        """Test loading when state file doesn't exist."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        state = manager.load()
        assert state.version == 1
        assert state.packages == []

    def test_save_and_load(self, tmp_path: Path) -> None:
        """Test saving and loading state."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        # Add a package
        pkg = Package(
            id="test-pkg",
            name="Test Package",
            description="A test",
            method=InstallMethod.CASK,
        )
        manager.add_installed_package(pkg, InstallSource.MAC_SETUP)

        # Load in a new manager
        manager2 = StateManager(state_file)
        state = manager2.load()

        assert len(state.packages) == 1
        assert state.packages[0].id == "test-pkg"
        assert state.packages[0].source == InstallSource.MAC_SETUP

    def test_add_installed_package(self, tmp_path: Path) -> None:
        """Test adding an installed package."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        pkg = Package(
            id="chrome",
            name="Google Chrome",
            description="Browser",
            method=InstallMethod.CASK,
        )
        manager.add_installed_package(pkg, InstallSource.MAC_SETUP, version="120.0")

        installed = manager.get_installed_package("chrome")
        assert installed is not None
        assert installed.name == "Google Chrome"
        assert installed.version == "120.0"
        assert installed.source == InstallSource.MAC_SETUP

    def test_remove_installed_package(self, tmp_path: Path) -> None:
        """Test removing an installed package."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        pkg = Package(
            id="test-pkg",
            name="Test",
            description="A test",
            method=InstallMethod.CASK,
        )
        manager.add_installed_package(pkg)

        assert manager.is_tracked("test-pkg") is True

        removed = manager.remove_installed_package("test-pkg")
        assert removed is True
        assert manager.is_tracked("test-pkg") is False

        # Removing non-existent package
        removed = manager.remove_installed_package("non-existent")
        assert removed is False

    def test_is_tracked(self, tmp_path: Path) -> None:
        """Test checking if package is tracked."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        assert manager.is_tracked("test-pkg") is False

        pkg = Package(
            id="test-pkg",
            name="Test",
            description="A test",
            method=InstallMethod.CASK,
        )
        manager.add_installed_package(pkg)

        assert manager.is_tracked("test-pkg") is True

    def test_get_mac_setup_packages(self, tmp_path: Path) -> None:
        """Test filtering packages by mac-setup source."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        pkg1 = Package(id="pkg1", name="Pkg 1", description="A", method=InstallMethod.CASK)
        pkg2 = Package(id="pkg2", name="Pkg 2", description="B", method=InstallMethod.CASK)
        pkg3 = Package(id="pkg3", name="Pkg 3", description="C", method=InstallMethod.FORMULA)

        manager.add_installed_package(pkg1, InstallSource.MAC_SETUP)
        manager.add_installed_package(pkg2, InstallSource.DETECTED)
        manager.add_installed_package(pkg3, InstallSource.MAC_SETUP)

        mac_setup_pkgs = manager.get_mac_setup_packages()
        assert len(mac_setup_pkgs) == 2
        assert all(p.source == InstallSource.MAC_SETUP for p in mac_setup_pkgs)

    def test_get_detected_packages(self, tmp_path: Path) -> None:
        """Test filtering packages by detected source."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        pkg1 = Package(id="pkg1", name="Pkg 1", description="A", method=InstallMethod.CASK)
        pkg2 = Package(id="pkg2", name="Pkg 2", description="B", method=InstallMethod.CASK)

        manager.add_installed_package(pkg1, InstallSource.MAC_SETUP)
        manager.add_installed_package(pkg2, InstallSource.DETECTED)

        detected = manager.get_detected_packages()
        assert len(detected) == 1
        assert detected[0].id == "pkg2"

    def test_clear(self, tmp_path: Path) -> None:
        """Test clearing all state."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        pkg = Package(id="test", name="Test", description="A", method=InstallMethod.CASK)
        manager.add_installed_package(pkg)

        assert len(manager.get_all_installed()) == 1

        manager.clear()
        assert len(manager.get_all_installed()) == 0

    def test_load_corrupt_state(self, tmp_path: Path) -> None:
        """Test loading a corrupt state file returns empty state."""
        state_file = tmp_path / "state.json"
        state_file.write_text("not valid json {{{")

        manager = StateManager(state_file)
        state = manager.load()

        assert state.packages == []

    def test_reload(self, tmp_path: Path) -> None:
        """Test reloading state from file."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        # Add and save
        pkg = Package(id="test", name="Test", description="A", method=InstallMethod.CASK)
        manager.add_installed_package(pkg)

        # Modify file externally
        import json
        data = json.loads(state_file.read_text())
        data["packages"].append({
            "id": "external",
            "name": "External",
            "method": "cask",
            "source": "detected",
            "installed_at": "2025-01-01T00:00:00",
        })
        state_file.write_text(json.dumps(data))

        # Reload should pick up changes
        manager.reload()
        assert manager.is_tracked("external") is True


class TestDetectInstalledPackages:
    """Tests for detect_installed_packages function."""

    def test_detect_homebrew_cask(self) -> None:
        """Test detecting installed Homebrew casks."""
        catalog = [
            Package(
                id="google-chrome", name="Chrome", description="Browser",
                method=InstallMethod.CASK
            ),
            Package(
                id="firefox", name="Firefox", description="Browser",
                method=InstallMethod.CASK
            ),
        ]
        homebrew_installed = ["google-chrome", "iterm2"]

        detected = detect_installed_packages(catalog, homebrew_installed)

        assert len(detected) == 1
        assert detected[0].id == "google-chrome"
        assert detected[0].source == InstallSource.DETECTED

    def test_detect_homebrew_formula(self) -> None:
        """Test detecting installed Homebrew formulas."""
        catalog = [
            Package(
                id="git", name="Git", description="VCS", method=InstallMethod.FORMULA
            ),
            Package(
                id="ripgrep", name="ripgrep", description="Search",
                method=InstallMethod.FORMULA
            ),
        ]
        homebrew_installed = ["git", "fd"]

        detected = detect_installed_packages(catalog, homebrew_installed)

        assert len(detected) == 1
        assert detected[0].id == "git"

    def test_detect_versioned_formula(self) -> None:
        """Test detecting versioned formulas like python@3.12."""
        catalog = [
            Package(
                id="python@3.12", name="Python 3.12", description="Python",
                method=InstallMethod.FORMULA
            ),
        ]
        # Homebrew might list it with or without version
        homebrew_installed = ["python@3.12"]

        detected = detect_installed_packages(catalog, homebrew_installed)

        assert len(detected) == 1
        assert detected[0].id == "python@3.12"

    def test_detect_mixed_sources(self) -> None:
        """Test detecting packages from multiple sources."""
        catalog = [
            Package(id="chrome", name="Chrome", description="Browser", method=InstallMethod.CASK),
            Package(id="git", name="Git", description="VCS", method=InstallMethod.FORMULA),
        ]
        homebrew_installed = ["chrome", "git"]

        detected = detect_installed_packages(catalog, homebrew_installed)

        assert len(detected) == 2


class TestSyncDetectedPackages:
    """Tests for sync_detected_packages function."""

    def test_sync_adds_new_detected(self, tmp_path: Path) -> None:
        """Test that sync adds newly detected packages."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        catalog = [
            Package(id="chrome", name="Chrome", description="Browser", method=InstallMethod.CASK),
        ]

        newly_detected = sync_detected_packages(manager, catalog, ["chrome"])

        assert len(newly_detected) == 1
        assert newly_detected[0].id == "chrome"
        assert manager.is_tracked("chrome") is True

    def test_sync_preserves_mac_setup_source(self, tmp_path: Path) -> None:
        """Test that sync doesn't change mac-setup packages to detected."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        # First, add as mac-setup installed
        pkg = Package(id="chrome", name="Chrome", description="Browser", method=InstallMethod.CASK)
        manager.add_installed_package(pkg, InstallSource.MAC_SETUP)

        catalog = [pkg]

        # Now sync - should not change source
        newly_detected = sync_detected_packages(manager, catalog, ["chrome"])

        assert len(newly_detected) == 0
        installed = manager.get_installed_package("chrome")
        assert installed is not None
        assert installed.source == InstallSource.MAC_SETUP

    def test_sync_no_duplicates(self, tmp_path: Path) -> None:
        """Test that sync doesn't create duplicate entries."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        catalog = [
            Package(id="chrome", name="Chrome", description="Browser", method=InstallMethod.CASK),
        ]

        # Sync twice
        sync_detected_packages(manager, catalog, ["chrome"])
        sync_detected_packages(manager, catalog, ["chrome"])

        assert len(manager.get_all_installed()) == 1
