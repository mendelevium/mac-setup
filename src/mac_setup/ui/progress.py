"""Progress tracking and display using Rich."""

from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from mac_setup.installers.base import InstallResult, InstallStatus

console = Console()


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

        # Progress bar
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        )
        self._task_id: TaskID | None = None

    def start(self) -> None:
        """Start the progress display."""
        self._progress.start()
        self._task_id = self._progress.add_task(
            "Installing packages...",
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
                description=f"Installing {package_name}...",
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

        # Print status
        if result.status == InstallStatus.SUCCESS:
            console.print(f"  [green]✓[/] {result.package_id}")
        elif result.status == InstallStatus.ALREADY_INSTALLED:
            console.print(f"  [blue]○[/] {result.package_id} (already installed)")
        elif result.status == InstallStatus.SKIPPED:
            console.print(f"  [yellow]○[/] {result.package_id} (skipped)")
        else:
            console.print(f"  [red]✗[/] {result.package_id}: {result.message}")

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

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold red]{task.description}"),
            BarColumn(complete_style="red", finished_style="red"),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        )
        self._task_id: TaskID | None = None

    def start(self) -> None:
        """Start the progress display."""
        self._progress.start()
        self._task_id = self._progress.add_task(
            "Uninstalling packages...",
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
                description=f"Uninstalling {package_name}...",
            )

    def complete_package(self, result: InstallResult, cleaned: bool = False) -> None:
        """Mark a package as complete."""
        self.completed.append(result)
        self.current += 1

        if self._task_id is not None:
            self._progress.update(self._task_id, completed=self.current)

        suffix = " (cleaned)" if cleaned else ""
        if result.status == InstallStatus.SUCCESS:
            console.print(f"  [green]✓[/] {result.package_id}{suffix}")
        elif result.status == InstallStatus.SKIPPED:
            console.print(f"  [yellow]○[/] {result.package_id} (skipped)")
        else:
            console.print(f"  [red]✗[/] {result.package_id}: {result.message}")


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

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold yellow]{task.description}"),
            BarColumn(complete_style="yellow", finished_style="yellow"),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        )
        self._task_id: TaskID | None = None

    def start(self) -> None:
        """Start the progress display."""
        self._progress.start()
        self._task_id = self._progress.add_task(
            "Updating packages...",
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
                description=f"Updating {package_name}...",
            )

    def complete_package(self, result: InstallResult) -> None:
        """Mark a package as complete."""
        self.completed.append(result)
        self.current += 1

        if self._task_id is not None:
            self._progress.update(self._task_id, completed=self.current)

        if result.status == InstallStatus.SUCCESS:
            version_info = f" -> {result.version}" if result.version else ""
            console.print(f"  [green]✓[/] {result.package_id}{version_info}")
        elif result.status == InstallStatus.ALREADY_INSTALLED:
            console.print(f"  [blue]○[/] {result.package_id} (already up to date)")
        elif result.status == InstallStatus.SKIPPED:
            console.print(f"  [yellow]○[/] {result.package_id} (skipped)")
        else:
            console.print(f"  [red]✗[/] {result.package_id}: {result.message}")


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
