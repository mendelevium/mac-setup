"""Preset management for mac-setup."""

from mac_setup.presets.manager import (
    PresetManager,
    load_preset,
    save_preset,
    list_presets,
    validate_preset,
)

__all__ = [
    "PresetManager",
    "load_preset",
    "save_preset",
    "list_presets",
    "validate_preset",
]
