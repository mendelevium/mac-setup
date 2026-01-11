"""Tests for preset management."""

from pathlib import Path

import pytest
import yaml

from mac_setup.models import Preset
from mac_setup.presets.manager import (
    PresetError,
    PresetManager,
    create_preset_from_selection,
    load_preset,
    save_preset,
    validate_preset,
)


class TestPresetManager:
    """Tests for PresetManager class."""

    def test_load_valid_preset(self, tmp_path: Path) -> None:
        """Test loading a valid preset file."""
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text(
            """
name: Test Preset
description: A test preset
packages:
  browsers:
    - google-chrome
  cli:
    - git
"""
        )

        manager = PresetManager()
        preset = manager.load(preset_file)

        assert preset.name == "Test Preset"
        assert preset.description == "A test preset"
        assert "browsers" in preset.packages
        assert "google-chrome" in preset.packages["browsers"]

    def test_load_missing_file(self, tmp_path: Path) -> None:
        """Test loading a non-existent preset file."""
        manager = PresetManager()

        with pytest.raises(PresetError) as exc_info:
            manager.load(tmp_path / "nonexistent.yaml")

        assert "not found" in str(exc_info.value)

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        """Test loading an invalid YAML file."""
        preset_file = tmp_path / "invalid.yaml"
        preset_file.write_text("{ invalid yaml [[[")

        manager = PresetManager()

        with pytest.raises(PresetError) as exc_info:
            manager.load(preset_file)

        assert "Invalid YAML" in str(exc_info.value)

    def test_load_invalid_preset_data(self, tmp_path: Path) -> None:
        """Test loading a YAML file with invalid preset structure."""
        preset_file = tmp_path / "invalid.yaml"
        preset_file.write_text("just a string, not a preset")

        manager = PresetManager()

        with pytest.raises(PresetError) as exc_info:
            manager.load(preset_file)

        assert "Invalid preset" in str(exc_info.value)

    def test_save_and_load_round_trip(self, tmp_path: Path) -> None:
        """Test saving and loading a preset."""
        from unittest.mock import patch

        preset = Preset(
            name="Round Trip Test",
            description="Testing save and load",
            packages={
                "browsers": ["google-chrome", "firefox"],
                "cli": ["git"],
            },
        )

        with patch("mac_setup.presets.manager.PRESETS_DIR", tmp_path):
            manager = PresetManager()
            saved_path = manager.save(preset, "round-trip")

            assert saved_path.exists()

            loaded = manager.load(saved_path)

            assert loaded.name == preset.name
            assert loaded.description == preset.description
            assert loaded.packages == preset.packages

    def test_save_sanitizes_filename(self, tmp_path: Path) -> None:
        """Test that save sanitizes filenames."""
        from unittest.mock import patch

        preset = Preset(
            name="My Preset With Spaces!",
            packages={},
        )

        with patch("mac_setup.presets.manager.PRESETS_DIR", tmp_path):
            manager = PresetManager()
            saved_path = manager.save(preset)

            assert saved_path.name == "mypresetwithspaces.yaml"

    def test_delete_preset(self, tmp_path: Path) -> None:
        """Test deleting a preset."""
        from unittest.mock import patch

        preset_file = tmp_path / "to-delete.yaml"
        preset_file.write_text("name: Delete Me\npackages: {}")

        with patch("mac_setup.presets.manager.PRESETS_DIR", tmp_path):
            manager = PresetManager()
            deleted = manager.delete("to-delete")

            assert deleted is True
            assert not preset_file.exists()

    def test_delete_nonexistent_preset(self, tmp_path: Path) -> None:
        """Test deleting a non-existent preset."""
        from unittest.mock import patch

        with patch("mac_setup.presets.manager.PRESETS_DIR", tmp_path):
            manager = PresetManager()
            deleted = manager.delete("nonexistent")

            assert deleted is False

    def test_validate_valid_preset(self) -> None:
        """Test validating a preset with valid packages."""
        preset = Preset(
            name="Valid",
            packages={
                "browsers": ["google-chrome", "firefox"],
                "cli": ["git", "ripgrep"],
            },
        )

        manager = PresetManager()
        warnings = manager.validate(preset)

        assert len(warnings) == 0

    def test_validate_invalid_packages(self) -> None:
        """Test validating a preset with invalid packages."""
        preset = Preset(
            name="Invalid",
            packages={
                "browsers": ["google-chrome", "nonexistent-browser"],
                "fake-category": ["some-package"],
            },
        )

        manager = PresetManager()
        warnings = manager.validate(preset)

        assert len(warnings) == 2
        assert any("nonexistent-browser" in w for w in warnings)
        assert any("fake-category" in w for w in warnings)

    def test_get_packages(self) -> None:
        """Test extracting packages from a preset."""
        preset = Preset(
            name="Test",
            packages={
                "browsers": ["google-chrome", "nonexistent"],
                "cli": ["git"],
            },
        )

        manager = PresetManager()
        packages = manager.get_packages(preset)

        # Should skip nonexistent package
        assert len(packages) == 2
        package_ids = [p.id for p in packages]
        assert "google-chrome" in package_ids
        assert "git" in package_ids
        assert "nonexistent" not in package_ids


class TestPresetFunctions:
    """Tests for module-level preset functions."""

    def test_load_preset_by_path(self, tmp_path: Path) -> None:
        """Test loading a preset by path."""
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text("name: Path Test\npackages: {}")

        preset = load_preset(preset_file)
        assert preset.name == "Path Test"

    def test_load_preset_by_string_path(self, tmp_path: Path) -> None:
        """Test loading a preset by string path."""
        preset_file = tmp_path / "test.yaml"
        preset_file.write_text("name: String Path Test\npackages: {}")

        preset = load_preset(str(preset_file))
        assert preset.name == "String Path Test"

    def test_save_preset_function(self, tmp_path: Path) -> None:
        """Test save_preset function."""
        from unittest.mock import patch

        preset = Preset(name="Save Test", packages={})

        with patch("mac_setup.presets.manager.PRESETS_DIR", tmp_path):
            path = save_preset(preset, "save-test")

            assert path.exists()
            assert (tmp_path / "save-test.yaml").exists()

    def test_validate_preset_function(self) -> None:
        """Test validate_preset function."""
        preset = Preset(
            name="Validate Test",
            packages={"browsers": ["google-chrome"]},
        )

        warnings = validate_preset(preset)
        assert len(warnings) == 0

    def test_create_preset_from_selection(self) -> None:
        """Test creating a preset from selection."""
        selection = {
            "browsers": ["google-chrome"],
            "cli": ["git", "ripgrep"],
        }

        preset = create_preset_from_selection(
            name="My Selection",
            selected_packages=selection,
            description="Custom selection",
            author="Test User",
        )

        assert preset.name == "My Selection"
        assert preset.description == "Custom selection"
        assert preset.author == "Test User"
        assert preset.packages == selection


class TestBuiltinPresets:
    """Tests for built-in presets."""

    def test_minimal_preset_exists(self) -> None:
        """Test that minimal preset exists and is valid."""
        from mac_setup.config import BUILTIN_PRESETS_DIR

        minimal_path = BUILTIN_PRESETS_DIR / "minimal.yaml"
        assert minimal_path.exists(), "minimal.yaml should exist"

        preset = load_preset(minimal_path)
        assert preset.name == "Minimal"

        # Validate packages
        warnings = validate_preset(preset)
        assert len(warnings) == 0, f"Minimal preset has invalid packages: {warnings}"

    def test_developer_preset_exists(self) -> None:
        """Test that developer preset exists and is valid."""
        from mac_setup.config import BUILTIN_PRESETS_DIR

        dev_path = BUILTIN_PRESETS_DIR / "developer.yaml"
        assert dev_path.exists(), "developer.yaml should exist"

        preset = load_preset(dev_path)
        assert preset.name == "Developer"

        warnings = validate_preset(preset)
        assert len(warnings) == 0, f"Developer preset has invalid packages: {warnings}"

    def test_creative_preset_exists(self) -> None:
        """Test that creative preset exists and is valid."""
        from mac_setup.config import BUILTIN_PRESETS_DIR

        creative_path = BUILTIN_PRESETS_DIR / "creative.yaml"
        assert creative_path.exists(), "creative.yaml should exist"

        preset = load_preset(creative_path)
        assert preset.name == "Creative"

        warnings = validate_preset(preset)
        assert len(warnings) == 0, f"Creative preset has invalid packages: {warnings}"

    def test_all_builtin_presets_valid(self) -> None:
        """Test that all built-in presets are valid."""
        from mac_setup.config import get_builtin_presets

        for preset_path in get_builtin_presets():
            preset = load_preset(preset_path)
            warnings = validate_preset(preset)
            assert len(warnings) == 0, f"{preset_path.name} has invalid packages: {warnings}"
