"""Application scanner for detecting installed apps in /Applications."""

from pathlib import Path


class ApplicationScanner:
    """Scans /Applications folder to detect installed applications."""

    APPLICATIONS_PATH = Path("/Applications")

    def __init__(self, applications_path: Path | None = None) -> None:
        """Initialize the scanner.

        Args:
            applications_path: Override path for testing
        """
        self._path = applications_path or self.APPLICATIONS_PATH
        self._installed_apps: set[str] | None = None

    def is_available(self) -> bool:
        """Check if the Applications folder exists."""
        return self._path.exists() and self._path.is_dir()

    def _refresh_cache(self) -> None:
        """Refresh the cache of installed apps."""
        self._installed_apps = set()
        if not self.is_available():
            return

        try:
            for item in self._path.iterdir():
                if item.suffix == ".app" and item.is_dir():
                    # Store the app name without .app extension
                    self._installed_apps.add(item.stem)
        except PermissionError:
            pass

    def list_installed_apps(self) -> set[str]:
        """Return set of app names in /Applications.

        Returns:
            Set of app names (without .app extension)
        """
        if self._installed_apps is None:
            self._refresh_cache()
        return self._installed_apps or set()

    def is_app_installed(self, app_name: str) -> bool:
        """Check if an app exists in /Applications.

        Args:
            app_name: The app name (without .app extension)

        Returns:
            True if app exists, False otherwise
        """
        return app_name in self.list_installed_apps()

    def invalidate_cache(self) -> None:
        """Invalidate the cache to force a refresh on next access."""
        self._installed_apps = None
