# mac-setup

Interactive CLI tool for provisioning new macOS machines with curated software selections.

## Features

- **Interactive Setup** - Browse categories and select packages with checkbox UI
- **Preset System** - Save and load configurations as YAML files
- **Dry Run Mode** - Preview all changes before executing
- **Progress Tracking** - Per-package and overall progress bars
- **Idempotent** - Safe to re-run, skips already-installed packages
- **Homebrew + Mac App Store** - Supports both via `brew` and `mas` CLI

## Requirements

- macOS
- Python 3.10+
- Homebrew (will prompt to install if missing)

## Installation

### Install from GitHub

```bash
pip install git+https://github.com/endelevium/mac-setup.git
```

### Local Development Install

```bash
git clone https://github.com/endelevium/mac-setup.git
cd mac-setup
pip install -e ".[dev]"
```

To install without development dependencies:

```bash
pip install -e .
```

## Usage

### Interactive Mode

```bash
mac-setup
```

Launches the interactive wizard with options to:
- Fresh Setup - Full interactive setup wizard
- Load Preset - Install from saved configuration
- Browse Packages - Explore categories and packages
- Uninstall - Remove installed packages
- Check Status - See what's installed

### Commands

```bash
mac-setup browse                      # Browse all packages by category
mac-setup install --preset developer  # Install from a preset
mac-setup install --preset ~/my.yaml  # Install from custom preset file
mac-setup presets                     # List available presets
mac-setup save my-setup               # Save current selection as preset
mac-setup status                      # Show installed packages
mac-setup uninstall                   # Interactive uninstall
mac-setup reset --confirm             # Uninstall all tracked packages
```

### Global Options

```bash
mac-setup --dry-run       # Preview changes without executing
mac-setup --yes           # Skip confirmation prompts
mac-setup --verbose       # Show detailed output
mac-setup --quiet         # Minimal output
mac-setup --help          # Show help
```

## Configuration

Configuration and state files are stored in `~/.config/mac-setup/`:

- `presets/` - Saved preset files (YAML)
- `state.json` - Tracks installed packages
- `logs/` - Installation logs

## Development

```bash
# Run tests
pytest

# Run a single test file
pytest tests/test_models.py

# Lint
ruff check src tests

# Format
ruff format src tests

# Type check
mypy src
```

## License

MIT
