# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mac-setup is an interactive CLI tool for provisioning new macOS machines with curated software selections. It provides a streamlined setup experience using Homebrew, featuring interactive package selection, presets, progress tracking, and uninstall capabilities.

## Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the CLI
mac-setup                           # Interactive mode
mac-setup browse                    # Browse packages
mac-setup install --preset NAME     # Install from preset
mac-setup status                    # Show installed packages

# Run tests
pytest                              # All tests
pytest tests/test_models.py         # Single test file
pytest -k "test_function_name"      # Single test by name

# Linting and type checking
ruff check src tests                # Lint
ruff format src tests               # Format
mypy src                            # Type check
```

## Architecture

### Core Data Flow

1. **Catalog** (`catalog.py`) - Static registry of all packages organized by category. Each `Package` has an `InstallMethod` (FORMULA or CASK) determining which installer handles it.

2. **Installers** (`installers/`) - Abstract `Installer` base class with implementations:
   - `HomebrewInstaller` - Handles both formulas and casks via `brew` CLI
   - Factory function `get_installer()` returns the correct installer for a method

3. **State Management** (`state.py`) - Tracks installed packages in `~/.config/mac-setup/state.json`. Distinguishes between packages installed via mac-setup (`MAC_SETUP`) and externally installed packages (`DETECTED`).

4. **Presets** (`presets/`) - YAML configurations saved to `~/.config/mac-setup/presets/`. Built-in presets in `presets/defaults/`.

### Key Models (`models.py`)

- `Package` - Single installable item with id, name, method
- `Category` - Group of related packages
- `Preset` - Saved configuration mapping category IDs to package ID lists
- `InstalledPackage` - State record with install source and timestamp
- `AppState` - Full state file with package list

### CLI Structure (`cli.py`)

Typer app with commands: `install`, `browse`, `presets`, `save`, `status`, `uninstall`, `reset`. Context object passes `--dry-run`, `--yes`, `--verbose` flags to subcommands.

### UI Components (`ui/`)

- `prompts.py` - questionary-based interactive prompts
- `display.py` - Rich panels, tables, status displays
- `progress.py` - Installation/uninstall progress bars

## Testing Patterns

Tests use pytest with fixtures in `conftest.py`. Common fixtures:
- `sample_package`, `sample_category`, `sample_preset` - Model instances
- `temp_config_dir` - Isolated config directory
- `mock_brew_*` - Mocked Homebrew command outputs

Installers are tested with mocked subprocess calls to avoid actual installations.
