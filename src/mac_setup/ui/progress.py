"""Progress tracking and display using Rich."""

from collections.abc import Generator
from contextlib import contextmanager
from enum import Enum

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

from mac_setup.installers.base import InstallResult, InstallStatus

console = Console()


class OperationType(str, Enum):
    """Type of package operation."""

    INSTALL = "install"
    UNINSTALL = "uninstall"
    UPDATE = "update"


# Configuration for each operation type
_OPERATION_CONFIG = {
    OperationType.INSTALL: {
        "color": "blue",
        "verb": "Installing",
        "noun": "Installing packages...",
    },
    OperationType.UNINSTALL: {
        "color": "red",
        "verb": "Uninstalling",
        "noun": "Uninstalling packages...",
    },
    OperationType.UPDATE: {
        "color": "yellow",
        "verb": "Updating",
        "noun": "Updating packages...",
    },
}


def _create_progress_bar(color: str) -> Progress:
    """Create a progress bar with the given color.

    Args:
        color: Rich color name for the progress bar

    Returns:
        Configured Progress instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[bold {color}]{{task.description}}"),
        BarColumn(complete_style=color, finished_style=color),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    )


def _format_result_status(
    result: InstallResult,
    operation: OperationType,
    cleaned: bool = False,
) -> str:
    """Format a result status message for display.

    Args:
        result: The operation result
        operation: Type of operation
        cleaned: Whether clean uninstall was performed (uninstall only)

    Returns:
        Formatted status string with Rich markup
    """
    if result.status == InstallStatus.SUCCESS:
        if operation == OperationType.UPDATE and result.version:
            return f"  [green]✓[/] {result.package_id} -> {result.version}"
        elif operation == OperationType.UNINSTALL and cleaned:
            return f"  [green]✓[/] {result.package_id} (cleaned)"
        return f"  [green]✓[/] {result.package_id}"
    elif result.status == InstallStatus.ALREADY_INSTALLED:
        if operation == OperationType.UPDATE:
            return f"  [blue]○[/] {result.package_id} (already up to date)"
        return f"  [blue]○[/] {result.package_id} (already installed)"
    elif result.status == InstallStatus.SKIPPED:
        return f"  [yellow]○[/] {result.package_id} (skipped)"
    else:
        return f"  [red]✗[/] {result.package_id}: {result.message}"


class InstallProgress:
    """Track and display installation progress."""

    def __init__(self, total_packages: int) -> None:
        """Initialize the progress tracker.

        Args:
            total_packages: Total number of packages to install
        """
        self.total = total_packages
        self.current = 0
        self.completed: list[InstallResult] = []
        self.current_package: str | None = None

        config = _OPERATION_CONFIG[OperationType.INSTALL]
        self._progress = _create_progress_bar(config["color"])
        self._config = config
        self._task_id: TaskID | None = None

    def start(self) -> None:
        """Start the progress display."""
        self._progress.start()
        self._task_id = self._progress.add_task(
            self._config["noun"],
            total=self.total,
        )

    def stop(self) -> None:
        """Stop the progress display."""
        self._progress.stop()

    def update(self, package_name: str) -> None:
        """Update progress for a new package.

        Args:
            package_name: Name of the package being installed
        """
        self.current_package = package_name
        if self._task_id is not None:
            self._progress.update(
                self._task_id,
                description=f"{self._config['verb']} {package_name}...",
            )

    def complete_package(self, result: InstallResult) -> None:
        """Mark a package as complete.

        Args:
            result: The installation result
        """
        self.completed.append(result)
        self.current += 1

        if self._task_id is not None:
            self._progress.update(
                self._task_id,
                completed=self.current,
            )

        console.print(_format_result_status(result, OperationType.INSTALL))

    @property
    def success_count(self) -> int:
        """Get count of successful installations."""
        return sum(1 for r in self.completed if r.status == InstallStatus.SUCCESS)

    @property
    def failed_count(self) -> int:
        """Get count of failed installations."""
        return sum(1 for r in self.completed if r.status == InstallStatus.FAILED)

    @property
    def skipped_count(self) -> int:
        """Get count of skipped packages."""
        return sum(
            1 for r in self.completed
            if r.status in (InstallStatus.SKIPPED, InstallStatus.ALREADY_INSTALLED)
        )


@contextmanager
def install_progress(total: int) -> Generator[InstallProgress, None, None]:
    """Context manager for installation progress.

    Args:
        total: Total number of packages

    Yields:
        InstallProgress instance
    """
    progress = InstallProgress(total)
    progress.start()
    try:
        yield progress
    finally:
        progress.stop()


class UninstallProgress:
    """Track and display uninstall progress."""

    def __init__(self, total_packages: int) -> None:
        """Initialize the progress tracker.

        Args:
            total_packages: Total number of packages to uninstall
        """
        self.total = total_packages
        self.current = 0
        self.completed: list[InstallResult] = []

        config = _OPERATION_CONFIG[OperationType.UNINSTALL]
        self._progress = _create_progress_bar(config["color"])
        self._config = config
        self._task_id: TaskID | None = None

    def start(self) -> None:
        """Start the progress display."""
        self._progress.start()
        self._task_id = self._progress.add_task(
            self._config["noun"],
            total=self.total,
        )

    def stop(self) -> None:
        """Stop the progress display."""
        self._progress.stop()

    def update(self, package_name: str) -> None:
        """Update progress for a new package."""
        if self._task_id is not None:
            self._progress.update(
                self._task_id,
                description=f"{self._config['verb']} {package_name}...",
            )

    def complete_package(self, result: InstallResult, cleaned: bool = False) -> None:
        """Mark a package as complete."""
        self.completed.append(result)
        self.current += 1

        if self._task_id is not None:
            self._progress.update(self._task_id, completed=self.current)

        console.print(_format_result_status(result, OperationType.UNINSTALL, cleaned))


@contextmanager
def uninstall_progress(total: int) -> Generator[UninstallProgress, None, None]:
    """Context manager for uninstall progress.

    Args:
        total: Total number of packages

    Yields:
        UninstallProgress instance
    """
    progress = UninstallProgress(total)
    progress.start()
    try:
        yield progress
    finally:
        progress.stop()


class UpdateProgress:
    """Track and display update progress."""

    def __init__(self, total_packages: int) -> None:
        """Initialize the progress tracker.

        Args:
            total_packages: Total number of packages to update
        """
        self.total = total_packages
        self.current = 0
        self.completed: list[InstallResult] = []

        config = _OPERATION_CONFIG[OperationType.UPDATE]
        self._progress = _create_progress_bar(config["color"])
        self._config = config
        self._task_id: TaskID | None = None

    def start(self) -> None:
        """Start the progress display."""
        self._progress.start()
        self._task_id = self._progress.add_task(
            self._config["noun"],
            total=self.total,
        )

    def stop(self) -> None:
        """Stop the progress display."""
        self._progress.stop()

    def update(self, package_name: str) -> None:
        """Update progress for a new package."""
        if self._task_id is not None:
            self._progress.update(
                self._task_id,
                description=f"{self._config['verb']} {package_name}...",
            )

    def complete_package(self, result: InstallResult) -> None:
        """Mark a package as complete."""
        self.completed.append(result)
        self.current += 1

        if self._task_id is not None:
            self._progress.update(self._task_id, completed=self.current)

        console.print(_format_result_status(result, OperationType.UPDATE))


@contextmanager
def update_progress(total: int) -> Generator[UpdateProgress, None, None]:
    """Context manager for update progress.

    Args:
        total: Total number of packages

    Yields:
        UpdateProgress instance
    """
    progress = UpdateProgress(total)
    progress.start()
    try:
        yield progress
    finally:
        progress.stop()


def print_spinner(message: str) -> None:
    """Print a message with a spinner (for single operations).

    Args:
        message: Message to display
    """
    with console.status(f"[bold blue]{message}[/]"):
        pass
