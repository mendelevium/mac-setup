"""Tests for package catalog."""


from mac_setup import catalog
from mac_setup.models import InstallMethod


class TestCatalogStructure:
    """Tests for catalog structure and integrity."""

    def test_all_categories_exist(self) -> None:
        """Test that all expected categories are present."""
        categories = catalog.get_all_categories()
        assert len(categories) == 19

        expected_ids = [
            "browsers",
            "editors",
            "terminals",
            "shells",
            "cli",
            "dev_tools",
            "languages",
            "package_managers",
            "coding_agents",
            "databases",
            "productivity",
            "communication",
            "creative",
            "cloud_devops",
            "virtualization",
            "writing",
            "system",
            "security",
            "fonts",
        ]
        category_ids = [cat.id for cat in categories]
        assert set(category_ids) == set(expected_ids)

    def test_each_category_has_packages(self) -> None:
        """Test that each category has at least one package."""
        for category in catalog.get_all_categories():
            assert len(category.packages) > 0, f"Category {category.id} has no packages"

    def test_each_package_has_required_fields(self) -> None:
        """Test that each package has all required fields."""
        for category in catalog.get_all_categories():
            for pkg in category.packages:
                assert pkg.id, f"Package in {category.id} missing id"
                assert pkg.name, f"Package {pkg.id} missing name"
                assert pkg.description, f"Package {pkg.id} missing description"
                assert pkg.method in InstallMethod, f"Package {pkg.id} has invalid method"

    def test_package_ids_are_unique(self) -> None:
        """Test that all package IDs are unique across categories."""
        seen_ids: set[str] = set()
        for category in catalog.get_all_categories():
            for pkg in category.packages:
                assert pkg.id not in seen_ids, f"Duplicate package ID: {pkg.id}"
                seen_ids.add(pkg.id)

    def test_mas_packages_have_mas_id(self) -> None:
        """Test that MAS packages have mas_id set."""
        for category in catalog.get_all_categories():
            for pkg in category.packages:
                if pkg.method == InstallMethod.MAS:
                    assert pkg.mas_id is not None, f"MAS package {pkg.id} missing mas_id"


class TestCatalogLookup:
    """Tests for catalog lookup functions."""

    def test_get_category_exists(self) -> None:
        """Test getting an existing category."""
        category = catalog.get_category("browsers")
        assert category is not None
        assert category.id == "browsers"
        assert category.name == "Browsers"

    def test_get_category_not_exists(self) -> None:
        """Test getting a non-existent category."""
        category = catalog.get_category("nonexistent")
        assert category is None

    def test_get_package_exists(self) -> None:
        """Test getting an existing package."""
        pkg = catalog.get_package("google-chrome")
        assert pkg is not None
        assert pkg.id == "google-chrome"
        assert pkg.name == "Google Chrome"
        assert pkg.method == InstallMethod.CASK

    def test_get_package_not_exists(self) -> None:
        """Test getting a non-existent package."""
        pkg = catalog.get_package("nonexistent-package")
        assert pkg is None

    def test_get_package_formula(self) -> None:
        """Test getting a formula package."""
        pkg = catalog.get_package("git")
        assert pkg is not None
        assert pkg.method == InstallMethod.FORMULA

    def test_get_package_mas(self) -> None:
        """Test getting a Mac App Store package."""
        pkg = catalog.get_package("amphetamine")
        assert pkg is not None
        assert pkg.method == InstallMethod.MAS
        assert pkg.mas_id == 937984704


class TestDefaultPackages:
    """Tests for default package selection."""

    def test_get_default_packages(self) -> None:
        """Test getting all default packages."""
        defaults = catalog.get_default_packages()
        assert len(defaults) > 0

        # All returned packages should be marked as default
        for pkg in defaults:
            assert pkg.default is True

    def test_default_packages_include_expected(self) -> None:
        """Test that expected default packages are included."""
        defaults = catalog.get_default_packages()
        default_ids = [pkg.id for pkg in defaults]

        # Check some expected defaults from spec
        expected_defaults = [
            "google-chrome",
            "visual-studio-code",
            "iterm2",
            "git",
            "gh",
            "ripgrep",
        ]
        for expected_id in expected_defaults:
            assert expected_id in default_ids, f"Expected default {expected_id} not found"


class TestPackageSearch:
    """Tests for package search functionality."""

    def test_search_by_name(self) -> None:
        """Test searching packages by name."""
        results = catalog.search_packages("Chrome")
        assert len(results) > 0
        assert any(pkg.id == "google-chrome" for pkg in results)

    def test_search_by_id(self) -> None:
        """Test searching packages by ID."""
        results = catalog.search_packages("visual-studio")
        assert len(results) > 0
        assert any(pkg.id == "visual-studio-code" for pkg in results)

    def test_search_by_description(self) -> None:
        """Test searching packages by description."""
        results = catalog.search_packages("fuzzy finder")
        assert len(results) > 0
        assert any(pkg.id == "fzf" for pkg in results)

    def test_search_case_insensitive(self) -> None:
        """Test that search is case-insensitive."""
        results_lower = catalog.search_packages("chrome")
        results_upper = catalog.search_packages("CHROME")
        assert len(results_lower) == len(results_upper)

    def test_search_no_results(self) -> None:
        """Test search with no matching results."""
        results = catalog.search_packages("xyznonexistent123")
        assert len(results) == 0

    def test_search_results_sorted(self) -> None:
        """Test that search results are sorted by name."""
        results = catalog.search_packages("git")
        names = [pkg.name for pkg in results]
        assert names == sorted(names)


class TestPackageCategory:
    """Tests for package-category relationship."""

    def test_get_package_category(self) -> None:
        """Test getting the category for a package."""
        category = catalog.get_package_category("google-chrome")
        assert category is not None
        assert category.id == "browsers"

    def test_get_package_category_not_exists(self) -> None:
        """Test getting category for non-existent package."""
        category = catalog.get_package_category("nonexistent")
        assert category is None


class TestPackageCounts:
    """Tests for package counting functions."""

    def test_total_package_count(self) -> None:
        """Test getting total package count."""
        count = catalog.get_total_package_count()
        assert count > 0

        # Verify count matches sum of all categories
        manual_count = sum(
            len(cat.packages) for cat in catalog.get_all_categories()
        )
        assert count == manual_count

    def test_packages_by_method(self) -> None:
        """Test getting packages by installation method."""
        formulas = catalog.get_packages_by_method(InstallMethod.FORMULA)
        casks = catalog.get_packages_by_method(InstallMethod.CASK)
        mas_apps = catalog.get_packages_by_method(InstallMethod.MAS)

        # Verify all returned packages have the correct method
        for pkg in formulas:
            assert pkg.method == InstallMethod.FORMULA
        for pkg in casks:
            assert pkg.method == InstallMethod.CASK
        for pkg in mas_apps:
            assert pkg.method == InstallMethod.MAS

        # Total should match
        total = catalog.get_total_package_count()
        assert len(formulas) + len(casks) + len(mas_apps) == total


class TestSpecificCategories:
    """Tests for specific category contents."""

    def test_browsers_category(self) -> None:
        """Test browsers category has expected packages."""
        category = catalog.get_category("browsers")
        assert category is not None
        package_ids = [pkg.id for pkg in category.packages]
        assert "google-chrome" in package_ids
        assert "firefox" in package_ids
        assert "arc" in package_ids

    def test_cli_utilities_category(self) -> None:
        """Test CLI utilities category has expected packages."""
        category = catalog.get_category("cli")
        assert category is not None
        package_ids = [pkg.id for pkg in category.packages]
        assert "git" in package_ids
        assert "ripgrep" in package_ids
        assert "fzf" in package_ids
        assert "jq" in package_ids

    def test_fonts_category(self) -> None:
        """Test fonts category packages have correct method."""
        category = catalog.get_category("fonts")
        assert category is not None
        for pkg in category.packages:
            # Fonts are installed as casks
            assert pkg.method == InstallMethod.CASK
            assert pkg.id.startswith("font-")
