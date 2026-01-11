"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from mac_setup.models import (
    AppState,
    Category,
    InstallMethod,
    InstalledPackage,
    InstallSource,
    Package,
    Preset,
)


class TestPackage:
    """Tests for Package model."""

    def test_package_creation_minimal(self) -> None:
        """Test creating a package with minimal required fields."""
        pkg = Package(
            id="test-pkg",
            name="Test Package",
            description="A test package",
        )
        assert pkg.id == "test-pkg"
        assert pkg.name == "Test Package"
        assert pkg.method == InstallMethod.CASK  # default
        assert pkg.default is False
        assert pkg.mas_id is None
        assert pkg.requires == []

    def test_package_creation_full(self) -> None:
        """Test creating a package with all fields."""
        pkg = Package(
            id="test-pkg",
            name="Test Package",
            description="A test package",
            method=InstallMethod.FORMULA,
            mas_id=None,
            default=True,
            requires=["dependency1", "dependency2"],
        )
        assert pkg.id == "test-pkg"
        assert pkg.method == InstallMethod.FORMULA
        assert pkg.default is True
        assert pkg.requires == ["dependency1", "dependency2"]

    def test_package_mas_app(self) -> None:
        """Test creating a Mac App Store package."""
        pkg = Package(
            id="amphetamine",
            name="Amphetamine",
            description="Keep Mac awake",
            method=InstallMethod.MAS,
            mas_id=937984704,
        )
        assert pkg.method == InstallMethod.MAS
        assert pkg.mas_id == 937984704

    def test_package_missing_required_fields(self) -> None:
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            Package(id="test")  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            Package(name="Test")  # type: ignore[call-arg]


class TestCategory:
    """Tests for Category model."""

    def test_category_creation(self, sample_package: Package) -> None:
        """Test creating a category with packages."""
        cat = Category(
            id="browsers",
            name="Browsers",
            description="Web browsers",
            icon="🌐",
            packages=[sample_package],
        )
        assert cat.id == "browsers"
        assert len(cat.packages) == 1
        assert cat.packages[0].id == sample_package.id

    def test_category_get_package(self, sample_category: Category) -> None:
        """Test getting a package by ID from category."""
        pkg = sample_category.get_package("test-app")
        assert pkg is not None
        assert pkg.id == "test-app"

        # Non-existent package
        pkg = sample_category.get_package("non-existent")
        assert pkg is None

    def test_category_get_default_packages(self, sample_category: Category) -> None:
        """Test getting default packages from category."""
        defaults = sample_category.get_default_packages()
        assert len(defaults) == 1
        assert defaults[0].id == "test-app"
        assert defaults[0].default is True


class TestPreset:
    """Tests for Preset model."""

    def test_preset_creation(self) -> None:
        """Test creating a preset."""
        preset = Preset(
            name="Developer",
            description="Full-stack development setup",
            packages={
                "browsers": ["google-chrome"],
                "editors": ["visual-studio-code", "cursor"],
            },
        )
        assert preset.name == "Developer"
        assert len(preset.packages) == 2
        assert "browsers" in preset.packages

    def test_preset_get_all_package_ids(self, sample_preset: Preset) -> None:
        """Test getting flat list of all package IDs."""
        ids = sample_preset.get_all_package_ids()
        assert "google-chrome" in ids
        assert "firefox" in ids
        assert "visual-studio-code" in ids
        assert len(ids) == 3

    def test_preset_package_count(self, sample_preset: Preset) -> None:
        """Test counting total packages in preset."""
        count = sample_preset.package_count()
        assert count == 3

    def test_preset_default_values(self) -> None:
        """Test preset default values are set correctly."""
        preset = Preset(name="Minimal", packages={})
        assert preset.version == 1
        assert preset.author is None
        assert preset.created is not None  # Auto-generated


class TestInstalledPackage:
    """Tests for InstalledPackage model."""

    def test_installed_package_creation(self) -> None:
        """Test creating an installed package record."""
        pkg = InstalledPackage(
            id="google-chrome",
            name="Google Chrome",
            method=InstallMethod.CASK,
            source=InstallSource.MAC_SETUP,
            version="120.0.6099.129",
        )
        assert pkg.id == "google-chrome"
        assert pkg.source == InstallSource.MAC_SETUP
        assert pkg.version == "120.0.6099.129"
        assert pkg.installed_at is not None

    def test_installed_package_detected_source(self) -> None:
        """Test installed package with detected source."""
        pkg = InstalledPackage(
            id="slack",
            name="Slack",
            method=InstallMethod.CASK,
            source=InstallSource.DETECTED,
        )
        assert pkg.source == InstallSource.DETECTED


class TestAppState:
    """Tests for AppState model."""

    def test_app_state_creation(self) -> None:
        """Test creating app state."""
        state = AppState()
        assert state.version == 1
        assert state.packages == []

    def test_app_state_add_package(self, sample_app_state: AppState) -> None:
        """Test adding a package to state."""
        new_pkg = InstalledPackage(
            id="new-app",
            name="New App",
            method=InstallMethod.CASK,
            source=InstallSource.MAC_SETUP,
        )
        sample_app_state.add_package(new_pkg)
        assert len(sample_app_state.packages) == 2

        # Adding same package should replace, not duplicate
        sample_app_state.add_package(new_pkg)
        assert len(sample_app_state.packages) == 2

    def test_app_state_remove_package(self, sample_app_state: AppState) -> None:
        """Test removing a package from state."""
        assert len(sample_app_state.packages) == 1
        removed = sample_app_state.remove_package("test-app")
        assert removed is True
        assert len(sample_app_state.packages) == 0

        # Removing non-existent package
        removed = sample_app_state.remove_package("non-existent")
        assert removed is False

    def test_app_state_get_package(self, sample_app_state: AppState) -> None:
        """Test getting a package from state."""
        pkg = sample_app_state.get_package("test-app")
        assert pkg is not None
        assert pkg.id == "test-app"

        pkg = sample_app_state.get_package("non-existent")
        assert pkg is None

    def test_app_state_filter_by_source(self) -> None:
        """Test filtering packages by source."""
        state = AppState(
            packages=[
                InstalledPackage(
                    id="app1",
                    name="App 1",
                    method=InstallMethod.CASK,
                    source=InstallSource.MAC_SETUP,
                ),
                InstalledPackage(
                    id="app2",
                    name="App 2",
                    method=InstallMethod.CASK,
                    source=InstallSource.DETECTED,
                ),
                InstalledPackage(
                    id="app3",
                    name="App 3",
                    method=InstallMethod.FORMULA,
                    source=InstallSource.MAC_SETUP,
                ),
            ]
        )

        mac_setup_pkgs = state.get_mac_setup_packages()
        assert len(mac_setup_pkgs) == 2
        assert all(p.source == InstallSource.MAC_SETUP for p in mac_setup_pkgs)

        detected_pkgs = state.get_detected_packages()
        assert len(detected_pkgs) == 1
        assert detected_pkgs[0].id == "app2"


class TestInstallMethod:
    """Tests for InstallMethod enum."""

    def test_install_method_values(self) -> None:
        """Test install method enum values."""
        assert InstallMethod.FORMULA.value == "formula"
        assert InstallMethod.CASK.value == "cask"
        assert InstallMethod.MAS.value == "mas"

    def test_install_method_string_comparison(self) -> None:
        """Test that enum values can be compared with strings."""
        assert InstallMethod.FORMULA == "formula"
        assert InstallMethod.CASK == "cask"
