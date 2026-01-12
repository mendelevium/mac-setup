"""Homebrew installer for formulas and casks."""

import shutil
import subprocess
from pathlib import Path

from mac_setup.installers.base import (
    Installer,
    InstallResult,
    InstallStatus,
    handle_subprocess_error,
)
from mac_setup.models import InstallMethod


class HomebrewInstaller(Installer):
    """Installer for Homebrew formulas and casks."""

    # Common paths for app support/preferences/caches
    CLEAN_UNINSTALL_PATHS = [
        Path.home() / "Library" / "Application Support",
        Path.home() / "Library" / "Preferences",
        Path.home() / "Library" / "Caches",
        Path.home() / "Library" / "Saved Application State",
        Path.home() / "Library" / "Logs",
    ]

    def __init__(self) -> None:
        """Initialize the Homebrew installer."""
        self._brew_path: str | None = None
        self._installed_formulas: set[str] | None = None
        self._installed_casks: set[str] | None = None

    def _invalidate_cache(self) -> None:
        """Invalidate the installed packages cache."""
        self._installed_formulas = None
        self._installed_casks = None

    @property
    def brew_path(self) -> str | None:
        """Get the path to the brew executable."""
        if self._brew_path is None:
            self._brew_path = shutil.which("brew")
        return self._brew_path

    def is_available(self) -> bool:
        """Check if Homebrew is installed."""
        return self.brew_path is not None

    def _run_brew(
        self, *args: str, capture_output: bool = True
    ) -> subprocess.CompletedProcess[str]:
        """Run a brew command.

        Args:
            *args: Arguments to pass to brew
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess with the result

        Raises:
            RuntimeError: If Homebrew is not available
        """
        if not self.brew_path:
            raise RuntimeError("Homebrew is not installed")

        return subprocess.run(
            [self.brew_path, *args],
            capture_output=capture_output,
            text=True,
            timeout=600,  # 10 minute timeout
        )

    def _refresh_installed_cache(self) -> None:
        """Refresh the cache of installed packages."""
        self._installed_formulas = set()
        self._installed_casks = set()

        try:
            # Get installed formulas
            result = self._run_brew("list", "--formula", "-1")
            if result.returncode == 0:
                self._installed_formulas = set(result.stdout.strip().split("\n"))
                # Remove empty strings
                self._installed_formulas.discard("")

            # Get installed casks
            result = self._run_brew("list", "--cask", "-1")
            if result.returncode == 0:
                self._installed_casks = set(result.stdout.strip().split("\n"))
                self._installed_casks.discard("")
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

    def _get_installed_set(self, method: InstallMethod) -> set[str]:
        """Get the set of installed packages for a method."""
        if self._installed_formulas is None or self._installed_casks is None:
            self._refresh_installed_cache()

        if method == InstallMethod.FORMULA:
            return self._installed_formulas or set()
        else:
            return self._installed_casks or set()

    def is_installed(self, package_id: str, method: InstallMethod = InstallMethod.CASK) -> bool:
        """Check if a package is installed.

        Args:
            package_id: The package identifier
            method: The installation method (formula or cask)

        Returns:
            True if installed, False otherwise
        """
        installed = self._get_installed_set(method)

        # Direct match
        if package_id in installed:
            return True

        # Handle versioned formulas (e.g., python@3.12 -> python)
        base_name = package_id.split("@")[0]
        if base_name in installed:
            return True

        # Reverse check: if package_id is "python", check if any "python@X" exists
        for pkg in installed:
            if pkg.startswith(f"{package_id}@"):
                return True

        return False

    def install(  # type: ignore[override]
        self, package_id: str, method: InstallMethod = InstallMethod.CASK, dry_run: bool = False
    ) -> InstallResult:
        """Install a Homebrew package.

        Args:
            package_id: The formula or cask name
            method: Whether to install as formula or cask
            dry_run: If True, don't actually install

        Returns:
            InstallResult with the outcome
        """
        if not self.is_available():
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.FAILED,
                message="Homebrew is not installed",
            )

        # Check if already installed
        if self.is_installed(package_id, method):
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.ALREADY_INSTALLED,
                message="Already installed",
            )

        if dry_run:
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.SKIPPED,
                message="Dry run - would install",
            )

        try:
            if method == InstallMethod.FORMULA:
                result = self._run_brew("install", package_id)
            else:
                result = self._run_brew("install", "--cask", package_id)

            self._invalidate_cache()

            if result.returncode == 0:
                version = self.get_version(package_id, method)
                return InstallResult(
                    package_id=package_id,
                    status=InstallStatus.SUCCESS,
                    message="Installed successfully",
                    version=version,
                )
            else:
                return InstallResult(
                    package_id=package_id,
                    status=InstallStatus.FAILED,
                    message=result.stderr or "Installation failed",
                )
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return handle_subprocess_error(package_id, e, "Installation")

    def uninstall(  # type: ignore[override]
        self,
        package_id: str,
        method: InstallMethod = InstallMethod.CASK,
        dry_run: bool = False,
        clean: bool = False,
    ) -> InstallResult:
        """Uninstall a Homebrew package.

        Args:
            package_id: The formula or cask name
            method: Whether package is formula or cask
            dry_run: If True, don't actually uninstall
            clean: If True, also remove app data directories

        Returns:
            InstallResult with the outcome
        """
        if not self.is_available():
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.FAILED,
                message="Homebrew is not installed",
            )

        if not self.is_installed(package_id, method):
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.SKIPPED,
                message="Not installed",
            )

        if dry_run:
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.SKIPPED,
                message="Dry run - would uninstall",
            )

        try:
            if method == InstallMethod.FORMULA:
                result = self._run_brew("uninstall", package_id)
            else:
                result = self._run_brew("uninstall", "--cask", package_id)

            self._invalidate_cache()

            if result.returncode == 0:
                # Perform clean uninstall if requested
                if clean and method == InstallMethod.CASK:
                    self._clean_app_data(package_id)

                return InstallResult(
                    package_id=package_id,
                    status=InstallStatus.SUCCESS,
                    message="Uninstalled successfully",
                )
            else:
                return InstallResult(
                    package_id=package_id,
                    status=InstallStatus.FAILED,
                    message=result.stderr or "Uninstallation failed",
                )
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return handle_subprocess_error(package_id, e, "Uninstallation")

    def update(
        self,
        package_id: str,
        method: InstallMethod = InstallMethod.CASK,
        dry_run: bool = False,
    ) -> InstallResult:
        """Update a Homebrew package to the latest version.

        Args:
            package_id: The formula or cask name
            method: Whether package is formula or cask
            dry_run: If True, don't actually update

        Returns:
            InstallResult with the outcome
        """
        if not self.is_available():
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.FAILED,
                message="Homebrew is not installed",
            )

        if not self.is_installed(package_id, method):
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.FAILED,
                message="Package is not installed",
            )

        if dry_run:
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.SKIPPED,
                message="Dry run - would update",
            )

        try:
            if method == InstallMethod.FORMULA:
                result = self._run_brew("upgrade", package_id)
            else:
                result = self._run_brew("upgrade", "--cask", package_id)

            self._invalidate_cache()

            if result.returncode == 0:
                version = self.get_version(package_id, method)
                return InstallResult(
                    package_id=package_id,
                    status=InstallStatus.SUCCESS,
                    message="Updated successfully",
                    version=version,
                )
            else:
                # Check if already up-to-date
                stderr_lower = result.stderr.lower() if result.stderr else ""
                if "already installed" in stderr_lower or "latest version" in stderr_lower:
                    return InstallResult(
                        package_id=package_id,
                        status=InstallStatus.ALREADY_INSTALLED,
                        message="Already up to date",
                    )
                return InstallResult(
                    package_id=package_id,
                    status=InstallStatus.FAILED,
                    message=result.stderr or "Update failed",
                )
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return handle_subprocess_error(package_id, e, "Update")

    def list_installed(self, method: InstallMethod | None = None) -> list[str]:
        """List installed Homebrew packages.

        Args:
            method: If specified, only list formula or cask packages

        Returns:
            List of installed package identifiers
        """
        if not self.is_available():
            return []

        if method is None:
            formulas = list(self._get_installed_set(InstallMethod.FORMULA))
            casks = list(self._get_installed_set(InstallMethod.CASK))
            return sorted(formulas + casks)
        else:
            return sorted(self._get_installed_set(method))

    def get_version(
        self, package_id: str, method: InstallMethod = InstallMethod.CASK
    ) -> str | None:
        """Get the installed version of a package."""
        if not self.is_available() or not self.is_installed(package_id, method):
            return None

        try:
            result = self._run_brew("info", "--json=v2", package_id)
            if result.returncode == 0:
                import json

                data = json.loads(result.stdout)
                if method == InstallMethod.FORMULA and data.get("formulae"):
                    formula = data["formulae"][0]
                    if formula.get("installed"):
                        version: str | None = formula["installed"][0].get("version")
                        return version
                elif method == InstallMethod.CASK and data.get("casks"):
                    cask = data["casks"][0]
                    # Fallback to available version if installed is not set
                    cask_version: str | None = cask.get("installed") or cask.get("version")
                    return cask_version
        except (subprocess.SubprocessError, json.JSONDecodeError, KeyError, IndexError):
            pass

        return None

    def get_versions_batch(
        self, packages: list[tuple[str, InstallMethod]]
    ) -> dict[str, str | None]:
        """Batch fetch versions for multiple packages.

        Args:
            packages: List of (package_id, method) tuples

        Returns:
            Dict mapping package_id to version (or None if not found)
        """
        if not self.is_available() or not packages:
            return {}

        # Separate formulas and casks
        formulas = [pkg_id for pkg_id, method in packages if method == InstallMethod.FORMULA]
        casks = [pkg_id for pkg_id, method in packages if method == InstallMethod.CASK]

        versions: dict[str, str | None] = {}

        try:
            import json

            # Fetch formula versions
            if formulas:
                result = self._run_brew("info", "--json=v2", *formulas)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for formula in data.get("formulae", []):
                        name = formula.get("name")
                        if name and formula.get("installed"):
                            versions[name] = formula["installed"][0].get("version")

            # Fetch cask versions
            if casks:
                result = self._run_brew("info", "--json=v2", "--cask", *casks)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for cask in data.get("casks", []):
                        token = cask.get("token")
                        if token:
                            # Fallback to available version if installed is not set
                            versions[token] = cask.get("installed") or cask.get("version")

        except (subprocess.SubprocessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass

        return versions

    def get_available_versions_batch(
        self, packages: list[tuple[str, InstallMethod]]
    ) -> dict[str, str | None]:
        """Batch fetch available (latest) versions for multiple packages.

        Args:
            packages: List of (package_id, method) tuples

        Returns:
            Dict mapping package_id to available version (or None if not found)
        """
        if not self.is_available() or not packages:
            return {}

        # Separate formulas and casks
        formulas = [pkg_id for pkg_id, method in packages if method == InstallMethod.FORMULA]
        casks = [pkg_id for pkg_id, method in packages if method == InstallMethod.CASK]

        versions: dict[str, str | None] = {}

        try:
            import json

            # Fetch formula available versions
            if formulas:
                result = self._run_brew("info", "--json=v2", *formulas)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for formula in data.get("formulae", []):
                        name = formula.get("name")
                        if name:
                            # Get stable version from versions object
                            versions_obj = formula.get("versions", {})
                            versions[name] = versions_obj.get("stable")

            # Fetch cask available versions
            if casks:
                result = self._run_brew("info", "--json=v2", "--cask", *casks)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for cask in data.get("casks", []):
                        token = cask.get("token")
                        if token:
                            # "version" field is the available version
                            versions[token] = cask.get("version")

        except (subprocess.SubprocessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass

        return versions

    def _clean_app_data(self, package_id: str) -> list[Path]:
        """Remove application data directories for a cask.

        Args:
            package_id: The cask identifier

        Returns:
            List of removed paths
        """
        removed: list[Path] = []
        # Convert cask ID to potential app names
        # e.g., "google-chrome" -> ["Google Chrome", "google-chrome", "GoogleChrome"]
        app_names = self._get_potential_app_names(package_id)

        for base_path in self.CLEAN_UNINSTALL_PATHS:
            if not base_path.exists():
                continue

            for app_name in app_names:
                app_path = base_path / app_name
                if app_path.exists():
                    try:
                        if app_path.is_dir():
                            shutil.rmtree(app_path)
                        else:
                            app_path.unlink()
                        removed.append(app_path)
                    except OSError:
                        pass  # Ignore permission errors

        return removed

    def _get_potential_app_names(self, package_id: str) -> list[str]:
        """Get potential application names for a cask ID.

        Args:
            package_id: The cask identifier

        Returns:
            List of potential app/bundle names
        """
        names: list[str] = [package_id]

        # Title case with spaces: google-chrome -> Google Chrome
        title_case = " ".join(word.title() for word in package_id.split("-"))
        names.append(title_case)

        # CamelCase: google-chrome -> GoogleChrome
        camel_case = "".join(word.title() for word in package_id.split("-"))
        names.append(camel_case)

        # Common bundle ID patterns
        names.append(f"com.{package_id.replace('-', '.')}")

        return names

    def get_clean_uninstall_paths(self, package_id: str) -> list[Path]:
        """Get paths that would be removed in a clean uninstall.

        Args:
            package_id: The cask identifier

        Returns:
            List of existing paths that would be removed
        """
        paths: list[Path] = []
        app_names = self._get_potential_app_names(package_id)

        for base_path in self.CLEAN_UNINSTALL_PATHS:
            if not base_path.exists():
                continue

            for app_name in app_names:
                app_path = base_path / app_name
                if app_path.exists():
                    paths.append(app_path)

        return paths


def install_homebrew() -> bool:
    """Install Homebrew if not present.

    Returns:
        True if Homebrew is now available, False otherwise
    """
    if shutil.which("brew"):
        return True

    try:
        # The official Homebrew install script
        install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        result = subprocess.run(
            install_script,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600,
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False
