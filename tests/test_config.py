"""Tests for configuration module."""

from pathlib import Path
from unittest.mock import patch

from mac_setup import config


class TestConfigPaths:
    """Tests for configuration paths."""

    def test_config_dir_path(self) -> None:
        """Test that CONFIG_DIR is in user's home directory."""
        assert config.CONFIG_DIR.parent.parent == Path.home()
        assert config.CONFIG_DIR.name == "mac-setup"
        assert ".config" in str(config.CONFIG_DIR)

    def test_presets_dir_path(self) -> None:
        """Test that PRESETS_DIR is under CONFIG_DIR."""
        assert config.PRESETS_DIR.parent == config.CONFIG_DIR
        assert config.PRESETS_DIR.name == "presets"

    def test_logs_dir_path(self) -> None:
        """Test that LOGS_DIR is under CONFIG_DIR."""
        assert config.LOGS_DIR.parent == config.CONFIG_DIR
        assert config.LOGS_DIR.name == "logs"

    def test_state_file_path(self) -> None:
        """Test that STATE_FILE is in CONFIG_DIR."""
        assert config.STATE_FILE.parent == config.CONFIG_DIR
        assert config.STATE_FILE.name == "state.json"

    def test_builtin_presets_dir(self) -> None:
        """Test that BUILTIN_PRESETS_DIR is within the package."""
        assert "mac_setup" in str(config.BUILTIN_PRESETS_DIR)
        assert config.BUILTIN_PRESETS_DIR.name == "defaults"


class TestEnsureDirectories:
    """Tests for directory creation."""

    def test_ensure_directories_creates_all(self, tmp_path: Path) -> None:
        """Test that ensure_directories creates all required directories."""
        with patch.object(config, "CONFIG_DIR", tmp_path / ".config" / "mac-setup"):
            with patch.object(config, "PRESETS_DIR", config.CONFIG_DIR / "presets"):
                with patch.object(config, "LOGS_DIR", config.CONFIG_DIR / "logs"):
                    config.ensure_directories()

                    assert config.CONFIG_DIR.exists()
                    assert config.PRESETS_DIR.exists()
                    assert config.LOGS_DIR.exists()

    def test_ensure_directories_idempotent(self, tmp_path: Path) -> None:
        """Test that ensure_directories is safe to call multiple times."""
        with patch.object(config, "CONFIG_DIR", tmp_path / ".config" / "mac-setup"):
            with patch.object(config, "PRESETS_DIR", config.CONFIG_DIR / "presets"):
                with patch.object(config, "LOGS_DIR", config.CONFIG_DIR / "logs"):
                    # Call twice - should not raise
                    config.ensure_directories()
                    config.ensure_directories()

                    assert config.CONFIG_DIR.exists()


class TestGetPresets:
    """Tests for preset discovery functions."""

    def test_get_user_presets_empty(self, tmp_path: Path) -> None:
        """Test getting user presets when directory is empty."""
        presets_dir = tmp_path / "presets"
        presets_dir.mkdir()

        with patch.object(config, "PRESETS_DIR", presets_dir):
            presets = config.get_user_presets()
            assert presets == []

    def test_get_user_presets_with_files(self, tmp_path: Path) -> None:
        """Test getting user presets with preset files."""
        presets_dir = tmp_path / "presets"
        presets_dir.mkdir()

        # Create some preset files
        (presets_dir / "developer.yaml").write_text("name: Developer")
        (presets_dir / "minimal.yaml").write_text("name: Minimal")
        (presets_dir / "not-yaml.txt").write_text("not a preset")  # Should be ignored

        with patch.object(config, "PRESETS_DIR", presets_dir):
            presets = config.get_user_presets()
            assert len(presets) == 2
            preset_names = [p.name for p in presets]
            assert "developer.yaml" in preset_names
            assert "minimal.yaml" in preset_names

    def test_get_user_presets_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test getting user presets when directory doesn't exist."""
        nonexistent = tmp_path / "nonexistent"

        with patch.object(config, "PRESETS_DIR", nonexistent):
            presets = config.get_user_presets()
            assert presets == []

    def test_get_builtin_presets_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test getting built-in presets when directory doesn't exist."""
        nonexistent = tmp_path / "nonexistent"

        with patch.object(config, "BUILTIN_PRESETS_DIR", nonexistent):
            presets = config.get_builtin_presets()
            assert presets == []

    def test_get_all_presets(self, tmp_path: Path) -> None:
        """Test getting all presets (built-in + user)."""
        builtin_dir = tmp_path / "builtin"
        user_dir = tmp_path / "user"
        builtin_dir.mkdir()
        user_dir.mkdir()

        (builtin_dir / "default.yaml").write_text("name: Default")
        (user_dir / "custom.yaml").write_text("name: Custom")

        with patch.object(config, "BUILTIN_PRESETS_DIR", builtin_dir):
            with patch.object(config, "PRESETS_DIR", user_dir):
                presets = config.get_all_presets()
                assert len(presets) == 2
                preset_names = [p.name for p in presets]
                assert "default.yaml" in preset_names
                assert "custom.yaml" in preset_names
