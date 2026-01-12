"""Mac App Store installer using mas-cli."""

import shutil
import subprocess

from mac_setup.installers.base import (
    Installer,
    InstallResult,
    InstallStatus,
    handle_subprocess_error,
)


class MASInstaller(Installer):
    """Installer for Mac App Store apps using mas-cli."""

    def __init__(self) -> None:
        """Initialize the MAS installer."""
        self._mas_path: str | None = None
        self._installed_apps: dict[int, str] | None = None

    @property
    def mas_path(self) -> str | None:
        """Get the path to the mas executable."""
        if self._mas_path is None:
            self._mas_path = shutil.which("mas")
        return self._mas_path

    def is_available(self) -> bool:
        """Check if mas-cli is installed."""
        return self.mas_path is not None

    def _run_mas(
        self, *args: str, capture_output: bool = True
    ) -> subprocess.CompletedProcess[str]:
        """Run a mas command.

        Args:
            *args: Arguments to pass to mas
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess with the result

        Raises:
            RuntimeError: If mas is not available
        """
        if not self.mas_path:
            raise RuntimeError("mas-cli is not installed")

        return subprocess.run(
            [self.mas_path, *args],
            capture_output=capture_output,
            text=True,
            timeout=300,  # 5 minute timeout
        )

    def _refresh_installed_cache(self) -> None:
        """Refresh the cache of installed apps."""
        self._installed_apps = {}

        if not self.is_available():
            return

        try:
            result = self._run_mas("list")
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                    # Format: "123456789 App Name (1.0.0)"
                    parts = line.split(" ", 1)
                    if len(parts) >= 2:
                        try:
                            app_id = int(parts[0])
                            # Extract name (remove version in parentheses)
                            name = parts[1].rsplit("(", 1)[0].strip()
                            self._installed_apps[app_id] = name
                        except ValueError:
                            continue
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

    def _get_installed_apps(self) -> dict[int, str]:
        """Get dictionary of installed apps (ID -> name)."""
        if self._installed_apps is None:
            self._refresh_installed_cache()
        return self._installed_apps or {}

    def is_installed(self, package_id: str, mas_id: int | None = None) -> bool:
        """Check if an app is installed.

        Args:
            package_id: The package identifier (not used for MAS, but required by interface)
            mas_id: The Mac App Store app ID

        Returns:
            True if installed, False otherwise
        """
        if mas_id is None:
            return False
        return mas_id in self._get_installed_apps()

    def install(  # type: ignore[override]
        self, package_id: str, mas_id: int | None = None, dry_run: bool = False
    ) -> InstallResult:
        """Install a Mac App Store app.

        Args:
            package_id: The package identifier (for result tracking)
            mas_id: The Mac App Store app ID
            dry_run: If True, don't actually install

        Returns:
            InstallResult with the outcome
        """
        if not self.is_available():
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.FAILED,
                message="mas-cli is not installed. Install it with: brew install mas",
            )

        if mas_id is None:
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.FAILED,
                message="No Mac App Store ID provided",
            )

        # Check if already installed
        if self.is_installed(package_id, mas_id):
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.ALREADY_INSTALLED,
                message="Already installed from App Store",
            )

        if dry_run:
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.SKIPPED,
                message="Dry run - would install from App Store",
            )

        try:
            result = self._run_mas("install", str(mas_id))

            # Invalidate cache after install
            self._installed_apps = None

            if result.returncode == 0:
                return InstallResult(
                    package_id=package_id,
                    status=InstallStatus.SUCCESS,
                    message="Installed from App Store",
                )
            else:
                # Check for common errors
                stderr = result.stderr or result.stdout or ""
                if "not signed in" in stderr.lower():
                    return InstallResult(
                        package_id=package_id,
                        status=InstallStatus.FAILED,
                        message="Not signed in to App Store. Please sign in first.",
                    )
                elif "already installed" in stderr.lower():
                    return InstallResult(
                        package_id=package_id,
                        status=InstallStatus.ALREADY_INSTALLED,
                        message="Already installed",
                    )
                else:
                    return InstallResult(
                        package_id=package_id,
                        status=InstallStatus.FAILED,
                        message=stderr or "Installation failed",
                    )
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return handle_subprocess_error(package_id, e, "Installation")

    def uninstall(  # type: ignore[override]
        self, package_id: str, mas_id: int | None = None, dry_run: bool = False
    ) -> InstallResult:
        """Uninstall a Mac App Store app.

        Note: mas-cli cannot uninstall apps. This returns a message directing
        the user to uninstall manually or use a tool like AppCleaner.

        Args:
            package_id: The package identifier
            mas_id: The Mac App Store app ID
            dry_run: If True, don't actually uninstall

        Returns:
            InstallResult with the outcome
        """
        if mas_id is None or not self.is_installed(package_id, mas_id):
            return InstallResult(
                package_id=package_id,
                status=InstallStatus.SKIPPED,
                message="Not installed or no App Store ID",
            )

        # mas-cli doesn't support uninstalling
        return InstallResult(
            package_id=package_id,
            status=InstallStatus.FAILED,
            message="App Store apps must be uninstalled manually. "
            "Drag the app to Trash or use AppCleaner.",
        )

    def list_installed(self) -> list[str]:
        """List installed Mac App Store apps.

        Returns:
            List of app names (not IDs, since we track by name)
        """
        if not self.is_available():
            return []

        apps = self._get_installed_apps()
        return sorted(apps.values())

    def list_installed_ids(self) -> list[int]:
        """List installed Mac App Store app IDs.

        Returns:
            List of app IDs
        """
        if not self.is_available():
            return []

        return list(self._get_installed_apps().keys())

    def get_version(self, package_id: str, mas_id: int | None = None) -> str | None:
        """Get the installed version of an app.

        Args:
            package_id: The package identifier
            mas_id: The Mac App Store app ID

        Returns:
            Version string if available, None otherwise
        """
        # mas list includes version info, but we'd need to parse it
        # For now, return None
        return None


def install_mas() -> bool:
    """Install mas-cli via Homebrew if not present.

    Returns:
        True if mas is now available, False otherwise
    """
    if shutil.which("mas"):
        return True

    brew_path = shutil.which("brew")
    if not brew_path:
        return False

    try:
        result = subprocess.run(
            [brew_path, "install", "mas"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False
