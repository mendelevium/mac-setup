"""Display functions using Rich for terminal output."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mac_setup import __version__
from mac_setup.installers.base import InstallResult, InstallStatus
from mac_setup.models import Category, InstalledPackage, Package

console = Console()


def print_banner() -> None:
    """Print the application banner."""
    banner_text = Text()
    banner_text.append("mac-setup", style="bold cyan")
    banner_text.append(f" v{__version__}\n", style="dim")
    banner_text.append("Interactive macOS Development Environment", style="italic")

    panel = Panel(
        banner_text,
        title="[bold white]Welcome[/]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[blue]INFO:[/] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]SUCCESS:[/] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]WARNING:[/] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]ERROR:[/] {message}")


def print_category_table(categories: list[Category], selected: set[str] | None = None) -> None:
    """Print a table of categories.

    Args:
        categories: List of categories to display
        selected: Set of selected category IDs (optional)
    """
    table = Table(title="Categories", show_header=True, header_style="bold magenta")
    table.add_column("", width=3)
    table.add_column("Category", style="cyan")
    table.add_column("Packages", justify="right")
    table.add_column("Description")

    for cat in categories:
        is_selected = selected and cat.id in selected
        check = "[green]✓[/]" if is_selected else " "
        table.add_row(
            check,
            f"{cat.icon} {cat.name}",
            str(len(cat.packages)),
            cat.description,
        )

    console.print(table)


def print_package_table(
    category: Category,
    installed: set[str] | None = None,
) -> None:
    """Print a table of packages in a category.

    Args:
        category: The category to display
        installed: Set of installed package IDs (optional)
    """
    table = Table(
        title=f"{category.icon} {category.name}",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Type", width=7)
    table.add_column("Package", style="cyan")
    table.add_column("Description")
    table.add_column("Status", justify="right")

    for pkg in category.packages:
        is_installed = installed and pkg.id in installed

        if is_installed:
            status = "[green]installed[/]"
        elif pkg.default:
            status = "[dim]default[/]"
        else:
            status = ""

        table.add_row(pkg.method.value, pkg.name, pkg.description, status)

    console.print(table)


def print_installed_packages(
    packages: list[InstalledPackage],
    available_versions: dict[str, str | None] | None = None,
    title: str = "Installed Packages",
) -> None:
    """Print a table of installed packages.

    Args:
        packages: List of installed packages
        available_versions: Dict mapping package_id to available version
        title: Table title
    """
    if not packages:
        console.print(f"[dim]No {title.lower()}[/]")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Package", style="cyan")
    table.add_column("Method")
    table.add_column("Installed")
    table.add_column("Current")

    for pkg in packages:
        installed_version = pkg.version or "-"
        current_version = "-"
        if available_versions and pkg.id in available_versions:
            current_version = available_versions[pkg.id] or "-"

        # Highlight if update available
        if pkg.version and current_version != "-" and pkg.version != current_version:
            current_version = f"[yellow]{current_version}[/]"

        table.add_row(
            pkg.name,
            pkg.method.value,
            installed_version,
            current_version,
        )

    console.print(table)


def print_install_plan(packages: list[Package], dry_run: bool = False) -> None:
    """Print the installation plan.

    Args:
        packages: Packages to be installed
        dry_run: Whether this is a dry run
    """
    title = "[yellow]DRY RUN -[/] Installation Plan" if dry_run else "Installation Plan"

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Package", style="cyan")
    table.add_column("Type")
    table.add_column("Description")

    for i, pkg in enumerate(packages, 1):
        table.add_row(
            str(i),
            pkg.name,
            pkg.method.value,
            pkg.description,
        )

    console.print(table)
    console.print(f"\n[bold]Total:[/] {len(packages)} packages")


def print_uninstall_plan(
    packages: list[InstalledPackage],
    clean: bool = False,
    dry_run: bool = False,
) -> None:
    """Print the uninstall plan.

    Args:
        packages: Packages to be uninstalled
        clean: Whether this is a clean uninstall
        dry_run: Whether this is a dry run
    """
    mode = "Clean Uninstall" if clean else "Standard Uninstall"
    title = f"[yellow]DRY RUN -[/] {mode} Plan" if dry_run else f"{mode} Plan"

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Package", style="cyan")
    table.add_column("Type")

    for i, pkg in enumerate(packages, 1):
        table.add_row(
            str(i),
            pkg.name,
            pkg.method.value,
        )

    console.print(table)
    console.print(f"\n[bold]Total:[/] {len(packages)} packages")

    if clean:
        console.print(
            "\n[yellow]Note:[/] Clean uninstall will also remove settings, caches, and data"
        )


def print_update_plan(
    packages: list[InstalledPackage],
    available_versions: dict[str, str | None],
    dry_run: bool = False,
) -> None:
    """Print the update plan.

    Args:
        packages: Packages to be updated
        available_versions: Dict mapping package_id to available version
        dry_run: Whether this is a dry run
    """
    title = "[yellow]DRY RUN -[/] Update Plan" if dry_run else "Update Plan"

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Package", style="cyan")
    table.add_column("Type")
    table.add_column("Installed")
    table.add_column("Available")

    for i, pkg in enumerate(packages, 1):
        current = pkg.version or "-"
        available = available_versions.get(pkg.id) or "-"
        table.add_row(
            str(i),
            pkg.name,
            pkg.method.value,
            current,
            f"[green]{available}[/]",
        )

    console.print(table)
    console.print(f"\n[bold]Total:[/] {len(packages)} packages to update")


def print_summary(
    results: list[InstallResult],
    operation: str = "Installation",
    elapsed_time: float | None = None,
) -> None:
    """Print a summary of installation/uninstall results.

    Args:
        results: List of installation results
        operation: Description of the operation (e.g., "Installation", "Uninstall")
        elapsed_time: Elapsed time in seconds (optional)
    """
    success_count = sum(1 for r in results if r.status == InstallStatus.SUCCESS)
    already_count = sum(1 for r in results if r.status == InstallStatus.ALREADY_INSTALLED)
    skipped_count = sum(1 for r in results if r.status == InstallStatus.SKIPPED)
    failed_count = sum(1 for r in results if r.status == InstallStatus.FAILED)

    # Build summary text
    lines = []
    action = "installed" if "Install" in operation else "removed"
    if success_count > 0:
        lines.append(f"[green]✓[/] {success_count} packages {action} successfully")
    if already_count > 0:
        lines.append(f"[blue]○[/] {already_count} packages already {action}")
    if skipped_count > 0:
        lines.append(f"[yellow]○[/] {skipped_count} packages skipped")
    if failed_count > 0:
        lines.append(f"[red]✗[/] {failed_count} packages failed")

    if elapsed_time is not None:
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        if minutes > 0:
            lines.append(f"\n[dim]Time elapsed: {minutes}m {seconds}s[/]")
        else:
            lines.append(f"\n[dim]Time elapsed: {seconds}s[/]")

    summary_text = "\n".join(lines)

    panel = Panel(
        summary_text,
        title=f"[bold]{operation} Complete[/]",
        border_style="green" if failed_count == 0 else "yellow",
        padding=(1, 2),
    )
    console.print(panel)

    # Show failed packages if any
    if failed_count > 0:
        console.print("\n[bold red]Failed packages:[/]")
        for result in results:
            if result.status == InstallStatus.FAILED:
                console.print(f"  [red]✗[/] {result.package_id}: {result.message}")


def print_status(
    mac_setup_packages: list[InstalledPackage],
    detected_packages: list[InstalledPackage],
    available_versions: dict[str, str | None] | None = None,
) -> None:
    """Print current status of installed packages.

    Args:
        mac_setup_packages: Packages installed via mac-setup
        detected_packages: Packages detected on system
        available_versions: Dict mapping package_id to available version
    """
    console.print()

    if mac_setup_packages:
        print_installed_packages(
            mac_setup_packages, available_versions, "Installed via mac-setup"
        )
        console.print()

    if detected_packages:
        print_installed_packages(
            detected_packages, available_versions, "Detected on System"
        )
        console.print()

    total = len(mac_setup_packages) + len(detected_packages)
    if total == 0:
        console.print("[dim]No tracked packages found[/]")
    else:
        console.print(f"[bold]Total tracked packages:[/] {total}")


def print_presets_table(presets: list[tuple[str, str, bool]]) -> None:
    """Print a table of available presets.

    Args:
        presets: List of (name, description, is_builtin) tuples
    """
    table = Table(title="Available Presets", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Type")

    for name, desc, is_builtin in presets:
        preset_type = "[dim]built-in[/]" if is_builtin else "[green]user[/]"
        table.add_row(name, desc, preset_type)

    console.print(table)
