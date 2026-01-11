"""Shared pytest fixtures for mac-setup tests."""

from pathlib import Path
from typing import Generator

import pytest

from mac_setup.models import (
    AppState,
    Category,
    InstallMethod,
    InstalledPackage,
    InstallSource,
    Package,
    Preset,
)


@pytest.fixture
def sample_package() -> Package:
    """Create a sample package for testing."""
    return Package(
        id="test-app",
        name="Test App",
        description="A test application",
        method=InstallMethod.CASK,
        default=True,
    )


@pytest.fixture
def sample_formula_package() -> Package:
    """Create a sample formula package for testing."""
    return Package(
        id="test-cli",
        name="Test CLI",
        description="A test CLI tool",
        method=InstallMethod.FORMULA,
        default=False,
    )


@pytest.fixture
def sample_mas_package() -> Package:
    """Create a sample Mac App Store package for testing."""
    return Package(
        id="test-mas-app",
        name="Test MAS App",
        description="A test Mac App Store app",
        method=InstallMethod.MAS,
        mas_id=123456789,
        default=False,
    )


@pytest.fixture
def sample_category(sample_package: Package, sample_formula_package: Package) -> Category:
    """Create a sample category with packages for testing."""
    return Category(
        id="test-category",
        name="Test Category",
        description="A test category",
        icon="🧪",
        packages=[sample_package, sample_formula_package],
    )


@pytest.fixture
def sample_preset() -> Preset:
    """Create a sample preset for testing."""
    return Preset(
        name="Test Preset",
        description="A test preset",
        author="Test Author",
        packages={
            "browsers": ["google-chrome", "firefox"],
            "editors": ["visual-studio-code"],
        },
    )


@pytest.fixture
def sample_installed_package() -> InstalledPackage:
    """Create a sample installed package for testing."""
    return InstalledPackage(
        id="test-app",
        name="Test App",
        method=InstallMethod.CASK,
        source=InstallSource.MAC_SETUP,
    )


@pytest.fixture
def sample_app_state(sample_installed_package: InstalledPackage) -> AppState:
    """Create a sample app state for testing."""
    return AppState(packages=[sample_installed_package])


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary config directory for testing."""
    config_dir = tmp_path / ".config" / "mac-setup"
    config_dir.mkdir(parents=True)
    yield config_dir


@pytest.fixture
def mock_brew_list_output() -> str:
    """Sample output from 'brew list --formula'."""
    return """git
ripgrep
fd
bat
fzf
jq
"""


@pytest.fixture
def mock_brew_cask_list_output() -> str:
    """Sample output from 'brew list --cask'."""
    return """google-chrome
visual-studio-code
iterm2
docker
slack
"""


@pytest.fixture
def mock_brew_info_output() -> str:
    """Sample output from 'brew info --json=v2'."""
    return """{
  "formulae": [],
  "casks": [
    {
      "token": "google-chrome",
      "version": "120.0.6099.129",
      "installed": "120.0.6099.129"
    }
  ]
}"""
