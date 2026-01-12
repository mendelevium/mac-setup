"""Preset management functionality."""

from pathlib import Path

import yaml

from mac_setup import catalog
from mac_setup.config import (
    BUILTIN_PRESETS_DIR,
    PRESETS_DIR,
    ensure_directories,
    get_builtin_presets,
    get_user_presets,
)
from mac_setup.models import Package, Preset


class PresetError(Exception):
    """Error related to preset operations."""

    pass


class PresetManager:
    """Manages preset loading, saving, and validation."""

    def __init__(self) -> None:
        """Initialize the preset manager."""
        ensure_directories()

    def list_available(self) -> list[tuple[str, str, bool]]:
        """List all available presets.

        Returns:
            List of (name, description, is_builtin) tuples
        """
        presets: list[tuple[str, str, bool]] = []

        # Built-in presets
        for path in get_builtin_presets():
            try:
                preset = self.load(path)
                presets.append((preset.name, preset.description or "", True))
            except PresetError:
                continue

        # User presets
        for path in get_user_presets():
            try:
                preset = self.load(path)
                presets.append((preset.name, preset.description or "", False))
            except PresetError:
                continue

        return presets

    def load(self, path: Path) -> Preset:
        """Load a preset from a file.

        Args:
            path: Path to the preset file

        Returns:
            Loaded Preset instance

        Raises:
            PresetError: If the preset cannot be loaded
        """
        if not path.exists():
            raise PresetError(f"Preset file not found: {path}")

        try:
            data = yaml.safe_load(path.read_text())
            if not isinstance(data, dict):
                raise PresetError(f"Invalid preset format: {path}")

            return Preset.model_validate(data)
        except yaml.YAMLError as e:
            raise PresetError(f"Invalid YAML in preset: {e}")
        except ValueError as e:
            raise PresetError(f"Invalid preset data: {e}")

    def load_by_name(self, name: str) -> Preset:
        """Load a preset by name.

        Args:
            name: Preset name (without .yaml extension)

        Returns:
            Loaded Preset instance

        Raises:
            PresetError: If the preset cannot be found
        """
        # Check user presets first
        user_path = PRESETS_DIR / f"{name}.yaml"
        if user_path.exists():
            return self.load(user_path)

        # Then check built-in presets
        builtin_path = BUILTIN_PRESETS_DIR / f"{name}.yaml"
        if builtin_path.exists():
            return self.load(builtin_path)

        raise PresetError(f"Preset not found: {name}")

    def save(self, preset: Preset, name: str | None = None) -> Path:
        """Save a preset to a file.

        Args:
            preset: The preset to save
            name: Optional file name (defaults to preset.name)

        Returns:
            Path to the saved file
        """
        ensure_directories()

        file_name = name or preset.name
        # Sanitize filename
        file_name = "".join(c for c in file_name if c.isalnum() or c in "-_")
        file_name = file_name.lower().replace(" ", "-")

        path = PRESETS_DIR / f"{file_name}.yaml"

        data = preset.model_dump(exclude_none=True)
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))

        return path

    def delete(self, name: str) -> bool:
        """Delete a user preset.

        Args:
            name: Preset name

        Returns:
            True if deleted, False if not found
        """
        path = PRESETS_DIR / f"{name}.yaml"
        if path.exists():
            path.unlink()
            return True
        return False

    def validate(self, preset: Preset) -> list[str]:
        """Validate a preset against the catalog.

        Args:
            preset: The preset to validate

        Returns:
            List of warning messages for invalid package IDs
        """
        warnings: list[str] = []

        for category_id, package_ids in preset.packages.items():
            category = catalog.get_category(category_id)
            if category is None:
                warnings.append(f"Unknown category: {category_id}")
                continue

            for pkg_id in package_ids:
                if catalog.get_package(pkg_id) is None:
                    warnings.append(f"Unknown package: {pkg_id} in {category_id}")

        return warnings

    def get_packages(self, preset: Preset) -> list[Package]:
        """Get all valid packages from a preset.

        Args:
            preset: The preset to extract packages from

        Returns:
            List of Package objects (skipping invalid IDs)
        """
        packages: list[Package] = []

        for package_ids in preset.packages.values():
            for pkg_id in package_ids:
                pkg = catalog.get_package(pkg_id)
                if pkg is not None:
                    packages.append(pkg)

        return packages


def load_preset(path_or_name: str | Path) -> Preset:
    """Load a preset from a path or by name.

    Args:
        path_or_name: File path or preset name

    Returns:
        Loaded Preset instance
    """
    manager = PresetManager()

    if isinstance(path_or_name, Path):
        return manager.load(path_or_name)

    # Check if it's a path
    path = Path(path_or_name)
    if path.exists():
        return manager.load(path)

    # Otherwise, treat as a name
    return manager.load_by_name(path_or_name)


def save_preset(preset: Preset, name: str | None = None) -> Path:
    """Save a preset to a file.

    Args:
        preset: The preset to save
        name: Optional file name

    Returns:
        Path to the saved file
    """
    manager = PresetManager()
    return manager.save(preset, name)


def list_presets() -> list[tuple[str, str, bool]]:
    """List all available presets.

    Returns:
        List of (name, description, is_builtin) tuples
    """
    manager = PresetManager()
    return manager.list_available()


def validate_preset(preset: Preset) -> list[str]:
    """Validate a preset against the catalog.

    Args:
        preset: The preset to validate

    Returns:
        List of warning messages
    """
    manager = PresetManager()
    return manager.validate(preset)


def create_preset_from_selection(
    name: str,
    selected_packages: dict[str, list[str]],
    description: str | None = None,
    author: str | None = None,
) -> Preset:
    """Create a preset from a package selection.

    Args:
        name: Preset name
        selected_packages: Dictionary of category_id -> [package_ids]
        description: Optional description
        author: Optional author

    Returns:
        New Preset instance
    """
    return Preset(
        name=name,
        description=description,
        author=author,
        packages=selected_packages,
    )
