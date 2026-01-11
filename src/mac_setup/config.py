"""Configuration and path management for mac-setup."""

from pathlib import Path

# Application directories
CONFIG_DIR = Path.home() / ".config" / "mac-setup"
PRESETS_DIR = CONFIG_DIR / "presets"
LOGS_DIR = CONFIG_DIR / "logs"
STATE_FILE = CONFIG_DIR / "state.json"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

# Built-in presets location (within package)
BUILTIN_PRESETS_DIR = Path(__file__).parent / "presets" / "defaults"


def ensure_directories() -> None:
    """Create all required directories if they don't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_user_presets() -> list[Path]:
    """Get list of user-created preset files."""
    if not PRESETS_DIR.exists():
        return []
    return sorted(PRESETS_DIR.glob("*.yaml"))


def get_builtin_presets() -> list[Path]:
    """Get list of built-in preset files."""
    if not BUILTIN_PRESETS_DIR.exists():
        return []
    return sorted(BUILTIN_PRESETS_DIR.glob("*.yaml"))


def get_all_presets() -> list[Path]:
    """Get all available presets (built-in + user)."""
    return get_builtin_presets() + get_user_presets()
