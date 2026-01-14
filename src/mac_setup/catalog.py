"""Package catalog - loads package data from catalog.yaml."""

from pathlib import Path

import yaml

from mac_setup.models import Category, InstallMethod, Package

# =============================================================================
# Catalog Loading
# =============================================================================

_CATALOG_PATH = Path(__file__).parent / "catalog.yaml"


def _load_catalog() -> list[Category]:
    """Load categories and packages from YAML file."""
    data = yaml.safe_load(_CATALOG_PATH.read_text())

    categories = []
    for cat_data in data["categories"]:
        packages = [
            Package(
                id=pkg["id"],
                name=pkg["name"],
                description=pkg["description"],
                method=InstallMethod(pkg.get("method", "cask")),
                app_name=pkg.get("app_name"),
                default=pkg.get("default", False),
                requires=pkg.get("requires", []),
            )
            for pkg in cat_data.get("packages", [])
        ]
        categories.append(
            Category(
                id=cat_data["id"],
                name=cat_data["name"],
                description=cat_data["description"],
                icon=cat_data.get("icon", ""),
                packages=packages,
            )
        )
    return categories


# Load catalog at module import time
ALL_CATEGORIES: list[Category] = _load_catalog()

# Build lookup maps for O(1) access
_CATEGORY_MAP: dict[str, Category] = {cat.id: cat for cat in ALL_CATEGORIES}
_PACKAGE_MAP: dict[str, Package] = {}
for category in ALL_CATEGORIES:
    for pkg in category.packages:
        _PACKAGE_MAP[pkg.id] = pkg


# =============================================================================
# Catalog Functions
# =============================================================================


def get_all_categories() -> list[Category]:
    """Get all available categories."""
    return ALL_CATEGORIES


def get_category(category_id: str) -> Category | None:
    """Get a category by ID."""
    return _CATEGORY_MAP.get(category_id)


def get_package(package_id: str) -> Package | None:
    """Get a package by ID from any category."""
    return _PACKAGE_MAP.get(package_id)


def get_default_packages() -> list[Package]:
    """Get all packages marked as default across all categories."""
    defaults: list[Package] = []
    for category in ALL_CATEGORIES:
        defaults.extend(category.get_default_packages())
    return defaults


def search_packages(query: str) -> list[Package]:
    """Search packages by name, ID, or description.

    Args:
        query: Search query (case-insensitive)

    Returns:
        List of matching packages
    """
    query_lower = query.lower()
    results: list[Package] = []

    for pkg in _PACKAGE_MAP.values():
        if (
            query_lower in pkg.id.lower()
            or query_lower in pkg.name.lower()
            or query_lower in pkg.description.lower()
        ):
            results.append(pkg)

    return sorted(results, key=lambda p: p.name)


def get_package_category(package_id: str) -> Category | None:
    """Get the category containing a package."""
    for category in ALL_CATEGORIES:
        if category.get_package(package_id):
            return category
    return None


def get_total_package_count() -> int:
    """Get total number of packages in the catalog."""
    return len(_PACKAGE_MAP)


def get_packages_by_method(method: InstallMethod) -> list[Package]:
    """Get all packages with a specific installation method."""
    return [pkg for pkg in _PACKAGE_MAP.values() if pkg.method == method]
