"""CLI commands for mac-setup."""

import time
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from mac_setup import __version__, catalog
from mac_setup.config import ensure_directories
from mac_setup.installers import ApplicationScanner, HomebrewInstaller, MASInstaller, get_installer
from mac_setup.installers.base import InstallResult, InstallStatus
from mac_setup.models import InstallMethod, InstalledPackage, InstallSource, Package
from mac_setup.presets import PresetManager, load_preset, save_preset, validate_preset
from mac_setup.presets.manager import PresetError, create_preset_from_selection
from mac_setup.state import StateManager, sync_detected_packages
from mac_setup.ui import (
    confirm,
    print_banner,
    print_error,
    print_info,
    print_success,
    print_warning,
    prompt_category_selection,
    prompt_main_menu,
    prompt_package_selection,
    prompt_preset_name,
    prompt_uninstall_mode,
)
from mac_setup.ui.display import (
    print_install_plan,
    print_status,
    print_summary,
    print_uninstall_plan,
    print_update_plan,
)
from mac_setup.ui.progress import install_progress, uninstall_progress, update_progress
from mac_setup.ui.prompts import (
    MainMenuChoice,
    UninstallMode,
    prompt_packages_to_uninstall,
    prompt_packages_to_update,
)

app = typer.Typer(
    name="mac-setup",
    help="Interactive macOS Development Environment Setup",
    no_args_is_help=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"mac-setup v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Preview changes without executing"),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompts"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed output"),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Minimal output"),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output"),
    ] = False,
) -> None:
    """Interactive macOS development environment setup."""
    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["yes"] = yes
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["no_color"] = no_color

    # If no subcommand, run interactive mode
    if ctx.invoked_subcommand is None:
        interactive_setup(ctx)


def interactive_setup(ctx: typer.Context) -> None:
    """Run the interactive setup wizard."""
    ensure_directories()
    print_banner()

    while True:
        choice = prompt_main_menu()

        if choice == MainMenuChoice.FRESH_SETUP:
            run_fresh_setup(ctx)
        elif choice == MainMenuChoice.LOAD_PRESET:
            run_load_preset(ctx)
        elif choice == MainMenuChoice.BROWSE:
            run_browse(ctx)
        elif choice == MainMenuChoice.UPDATE:
            run_update_interactive(ctx)
        elif choice == MainMenuChoice.UNINSTALL:
            run_uninstall_interactive(ctx)
        elif choice == MainMenuChoice.STATUS:
            run_status()
        elif choice == MainMenuChoice.EXIT:
            print_info("Goodbye!")
            break


def run_fresh_setup(ctx: typer.Context) -> None:
    """Run the fresh setup wizard."""
    dry_run = ctx.obj.get("dry_run", False)
    skip_confirm = ctx.obj.get("yes", False)

    # Get all categories
    categories = catalog.get_all_categories()

    # Select categories
    selected_categories = prompt_category_selection(categories)
    if not selected_categories:
        print_warning("No categories selected")
        return

    # Collect packages from each category
    all_selected_packages: dict[str, list[str]] = {}

    # Get installed packages for display
    homebrew = HomebrewInstaller()
    installed_ids: set[str] = set()
    if homebrew.is_available():
        installed_ids.update(homebrew.list_installed())

    for cat_id in selected_categories:
        cat = catalog.get_category(cat_id)
        if cat is None:
            continue

        package_ids = prompt_package_selection(cat, installed=installed_ids)
        if package_ids:
            all_selected_packages[cat_id] = package_ids

    if not all_selected_packages:
        print_warning("No packages selected")
        return

    # Flatten to package list
    packages_to_install: list[Package] = []
    for pkg_ids in all_selected_packages.values():
        for pkg_id in pkg_ids:
            pkg = catalog.get_package(pkg_id)
            if pkg:
                packages_to_install.append(pkg)

    # Install
    _run_installation(packages_to_install, dry_run, skip_confirm)

    # Offer to save as preset
    if not dry_run and confirm("Would you like to save this configuration as a preset?"):
        name = prompt_preset_name()
        if name:
            preset = create_preset_from_selection(name, all_selected_packages)
            path = save_preset(preset)
            print_success(f"Preset saved to {path}")


def run_load_preset(ctx: typer.Context) -> None:
    """Run installation from a preset."""
    dry_run = ctx.obj.get("dry_run", False)
    skip_confirm = ctx.obj.get("yes", False)

    manager = PresetManager()
    available = manager.list_available()

    if not available:
        print_warning("No presets available")
        return

    from mac_setup.ui.prompts import prompt_preset_selection

    presets_for_prompt = [(name, desc) for name, desc, _ in available]
    selected = prompt_preset_selection(presets_for_prompt)

    if not selected:
        return

    # Load and install
    try:
        preset = manager.load_by_name(selected)
    except PresetError as e:
        print_error(str(e))
        return

    # Validate
    warnings = manager.validate(preset)
    if warnings:
        for warning in warnings:
            print_warning(warning)

    packages = manager.get_packages(preset)
    if not packages:
        print_warning("Preset contains no valid packages")
        return

    _run_installation(packages, dry_run, skip_confirm)


def run_browse(ctx: typer.Context) -> None:
    """Browse categories and packages."""
    categories = catalog.get_all_categories()

    # Get installed for display (from Homebrew and /Applications)
    homebrew = HomebrewInstaller()
    scanner = ApplicationScanner()

    installed_ids: set[str] = set()
    if homebrew.is_available():
        installed_ids.update(homebrew.list_installed())

    # Also detect apps from /Applications using app_name
    if scanner.is_available():
        installed_apps = scanner.list_installed_apps()
        for cat in categories:
            for pkg in cat.packages:
                if pkg.app_name and pkg.app_name in installed_apps:
                    installed_ids.add(pkg.id)

    selected_categories = prompt_category_selection(categories)

    for cat_id in selected_categories:
        cat = catalog.get_category(cat_id)
        if cat:
            from mac_setup.ui.display import print_package_table

            print_package_table(cat, installed=installed_ids)
            console.print()


def run_uninstall_interactive(ctx: typer.Context) -> None:
    """Run interactive uninstall."""
    dry_run = ctx.obj.get("dry_run", False)
    skip_confirm = ctx.obj.get("yes", False)

    state_manager = StateManager()
    all_packages = state_manager.get_all_installed()

    if not all_packages:
        print_info("No tracked packages to uninstall")
        return

    # Select packages
    selected_ids = prompt_packages_to_uninstall(all_packages)
    if not selected_ids:
        print_warning("No packages selected")
        return

    # Select mode
    mode = prompt_uninstall_mode()
    clean = mode == UninstallMode.CLEAN

    # Get selected packages
    packages_to_remove = [p for p in all_packages if p.id in selected_ids]

    # Show plan
    print_uninstall_plan(packages_to_remove, clean=clean, dry_run=dry_run)

    if not skip_confirm and not confirm("Proceed with uninstall?"):
        print_info("Uninstall cancelled")
        return

    # Run uninstall
    _run_uninstallation(packages_to_remove, clean, dry_run, state_manager)


def run_status() -> None:
    """Show current installation status."""
    state_manager = StateManager()

    # Sync detected packages
    homebrew = HomebrewInstaller()
    mas = MASInstaller()
    scanner = ApplicationScanner()

    homebrew_installed = homebrew.list_installed() if homebrew.is_available() else []
    mas_installed = mas.list_installed_ids() if mas.is_available() else []

    all_catalog_packages = [pkg for cat in catalog.get_all_categories() for pkg in cat.packages]
    sync_detected_packages(
        state_manager, all_catalog_packages, homebrew_installed, mas_installed, homebrew, scanner
    )

    mac_setup_pkgs = state_manager.get_mac_setup_packages()
    detected_pkgs = state_manager.get_detected_packages()

    # Fetch available versions for all packages
    all_pkgs = mac_setup_pkgs + detected_pkgs
    available_versions: dict[str, str | None] = {}

    if homebrew.is_available() and all_pkgs:
        homebrew_packages = [
            (pkg.id, pkg.method)
            for pkg in all_pkgs
            if pkg.method in (InstallMethod.FORMULA, InstallMethod.CASK)
        ]
        if homebrew_packages:
            available_versions = homebrew.get_available_versions_batch(homebrew_packages)

    print_status(mac_setup_pkgs, detected_pkgs, available_versions)


@app.command()
def install(
    ctx: typer.Context,
    preset: Annotated[
        Optional[str],
        typer.Option("--preset", "-p", help="Preset name or path to YAML file"),
    ] = None,
    category: Annotated[
        Optional[str],
        typer.Option("--category", "-c", help="Filter by category (comma-separated)"),
    ] = None,
) -> None:
    """Install packages from a preset or selection."""
    dry_run = ctx.obj.get("dry_run", False)
    skip_confirm = ctx.obj.get("yes", False)

    if preset:
        # Install from preset
        try:
            loaded = load_preset(preset)
        except PresetError as e:
            print_error(str(e))
            raise typer.Exit(1)

        manager = PresetManager()
        packages = manager.get_packages(loaded)

        # Filter by category if specified
        if category:
            cat_filter = set(c.strip() for c in category.split(","))
            packages = [p for p in packages if catalog.get_package_category(p.id) and
                       catalog.get_package_category(p.id).id in cat_filter]  # type: ignore

        if not packages:
            print_warning("No packages to install")
            raise typer.Exit(0)

        _run_installation(packages, dry_run, skip_confirm)
    else:
        # Interactive selection
        run_fresh_setup(ctx)


@app.command()
def browse() -> None:
    """Browse available packages by category."""
    categories = catalog.get_all_categories()

    homebrew = HomebrewInstaller()
    installed_ids: set[str] = set()
    if homebrew.is_available():
        installed_ids.update(homebrew.list_installed())

    for cat in categories:
        from mac_setup.ui.display import print_package_table

        print_package_table(cat, installed=installed_ids)
        console.print()


@app.command()
def presets() -> None:
    """List available presets."""
    manager = PresetManager()
    available = manager.list_available()

    if not available:
        print_info("No presets available")
        return

    from rich.table import Table

    table = Table(title="Available Presets", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Type")

    for name, desc, is_builtin in available:
        preset_type = "[dim]built-in[/]" if is_builtin else "[green]user[/]"
        table.add_row(name, desc, preset_type)

    console.print(table)


@app.command(name="save")
def save_command(
    name: Annotated[str, typer.Argument(help="Name for the preset")],
) -> None:
    """Save current selection as a preset."""
    # Interactive package selection
    categories = catalog.get_all_categories()
    selected_categories = prompt_category_selection(categories)

    if not selected_categories:
        print_warning("No categories selected")
        raise typer.Exit(0)

    all_selected: dict[str, list[str]] = {}
    for cat_id in selected_categories:
        cat = catalog.get_category(cat_id)
        if cat:
            package_ids = prompt_package_selection(cat)
            if package_ids:
                all_selected[cat_id] = package_ids

    if not all_selected:
        print_warning("No packages selected")
        raise typer.Exit(0)

    preset = create_preset_from_selection(name, all_selected)
    path = save_preset(preset)
    print_success(f"Preset saved to {path}")


@app.command()
def status() -> None:
    """Show installed packages status."""
    run_status()


@app.command()
def update(
    ctx: typer.Context,
    all_packages: Annotated[
        bool,
        typer.Option("--all", "-a", help="Update all outdated packages"),
    ] = False,
) -> None:
    """Update packages to their latest versions."""
    dry_run = ctx.obj.get("dry_run", False)
    skip_confirm = ctx.obj.get("yes", False)

    state_manager = StateManager()
    homebrew = HomebrewInstaller()

    if not homebrew.is_available():
        print_error("Homebrew is not installed")
        raise typer.Exit(1)

    # Get all installed packages
    all_installed = state_manager.get_all_installed()

    if not all_installed:
        print_info("No tracked packages to update")
        raise typer.Exit(0)

    # Get Homebrew packages only (MAS updates not supported via this tool)
    homebrew_packages = [
        pkg for pkg in all_installed
        if pkg.method in (InstallMethod.FORMULA, InstallMethod.CASK)
    ]

    if not homebrew_packages:
        print_info("No Homebrew packages to update")
        raise typer.Exit(0)

    # Fetch installed and available versions
    pkg_tuples = [(pkg.id, pkg.method) for pkg in homebrew_packages]
    installed_versions = homebrew.get_versions_batch(pkg_tuples)
    available_versions = homebrew.get_available_versions_batch(pkg_tuples)

    # Update the packages with their current installed versions
    for pkg in homebrew_packages:
        if pkg.id in installed_versions:
            pkg.version = installed_versions[pkg.id]

    # Find outdated packages
    outdated_packages = []
    for pkg in homebrew_packages:
        installed = pkg.version
        available = available_versions.get(pkg.id)
        if installed and available and installed != available:
            outdated_packages.append(pkg)

    if not outdated_packages:
        print_info("All packages are up to date")
        raise typer.Exit(0)

    # Show update plan
    print_info(f"Found {len(outdated_packages)} outdated package(s)")
    print_update_plan(outdated_packages, available_versions, dry_run=dry_run)

    if not all_packages:
        # Without --all flag, just show the plan
        print_info("Use --all or -a to update all outdated packages")
        raise typer.Exit(0)

    if not skip_confirm and not confirm(f"Update {len(outdated_packages)} packages?"):
        print_info("Update cancelled")
        raise typer.Exit(0)

    if dry_run:
        print_info("Dry run - no changes made")
        raise typer.Exit(0)

    # Run updates
    _run_updates(outdated_packages, available_versions, state_manager, homebrew)


def run_update_interactive(ctx: typer.Context) -> None:
    """Run interactive update (called from main menu)."""
    dry_run = ctx.obj.get("dry_run", False)
    skip_confirm = ctx.obj.get("yes", False)

    state_manager = StateManager()
    homebrew = HomebrewInstaller()

    if not homebrew.is_available():
        print_error("Homebrew is not installed")
        return

    # Get all installed packages
    all_installed = state_manager.get_all_installed()

    if not all_installed:
        print_info("No tracked packages to update")
        return

    # Get Homebrew packages only
    homebrew_packages = [
        pkg for pkg in all_installed
        if pkg.method in (InstallMethod.FORMULA, InstallMethod.CASK)
    ]

    if not homebrew_packages:
        print_info("No Homebrew packages to update")
        return

    # Fetch installed and available versions
    pkg_tuples = [(pkg.id, pkg.method) for pkg in homebrew_packages]
    installed_versions = homebrew.get_versions_batch(pkg_tuples)
    available_versions = homebrew.get_available_versions_batch(pkg_tuples)

    # Update the packages with their current installed versions
    for pkg in homebrew_packages:
        if pkg.id in installed_versions:
            pkg.version = installed_versions[pkg.id]

    # Find outdated packages
    outdated_packages = []
    for pkg in homebrew_packages:
        installed = pkg.version
        available = available_versions.get(pkg.id)
        if installed and available and installed != available:
            outdated_packages.append(pkg)

    if not outdated_packages:
        print_info("All packages are up to date")
        return

    # Prompt user to select packages to update
    print_info(f"Found {len(outdated_packages)} outdated package(s)")
    selected_ids = prompt_packages_to_update(outdated_packages, available_versions)

    if not selected_ids:
        print_info("No packages selected")
        return

    # Filter to selected packages
    packages_to_update = [pkg for pkg in outdated_packages if pkg.id in selected_ids]

    # Show update plan
    print_update_plan(packages_to_update, available_versions, dry_run=dry_run)

    if not skip_confirm and not confirm(f"Update {len(packages_to_update)} packages?"):
        print_info("Update cancelled")
        return

    if dry_run:
        print_info("Dry run - no changes made")
        return

    # Run updates
    _run_updates(packages_to_update, available_versions, state_manager, homebrew)


def _run_updates(
    packages: list[InstalledPackage],
    available_versions: dict[str, str | None],
    state_manager: StateManager,
    homebrew: HomebrewInstaller,
) -> None:
    """Run package updates.

    Args:
        packages: Packages to update
        available_versions: Dict of available versions
        state_manager: State manager instance
        homebrew: Homebrew installer instance
    """
    results: list[InstallResult] = []
    start_time = time.time()

    with update_progress(len(packages)) as progress:
        for pkg in packages:
            progress.update(pkg.name)

            result = homebrew.update(pkg.id, pkg.method)
            results.append(result)
            progress.complete_package(result)

            # Update version in state if successful
            if result.status == InstallStatus.SUCCESS and result.version:
                existing = state_manager.get_installed_package(pkg.id)
                if existing:
                    existing.version = result.version
                    state_manager.save()

    elapsed = time.time() - start_time
    print_summary(results, "Update", elapsed)


@app.command()
def uninstall(
    ctx: typer.Context,
    packages: Annotated[
        Optional[str],
        typer.Option("--packages", "-p", help="Specific packages to uninstall (comma-separated)"),
    ] = None,
    clean: Annotated[
        bool,
        typer.Option("--clean", "-c", help="Remove all associated files (settings, caches, data)"),
    ] = False,
) -> None:
    """Uninstall packages."""
    dry_run = ctx.obj.get("dry_run", False)
    skip_confirm = ctx.obj.get("yes", False)

    state_manager = StateManager()

    if packages:
        # Uninstall specific packages
        pkg_ids = [p.strip() for p in packages.split(",")]
        packages_to_remove = [
            p for p in state_manager.get_all_installed() if p.id in pkg_ids
        ]

        if not packages_to_remove:
            print_warning("No tracked packages found matching the specified IDs")
            raise typer.Exit(0)
    else:
        # Interactive selection
        run_uninstall_interactive(ctx)
        return

    print_uninstall_plan(packages_to_remove, clean=clean, dry_run=dry_run)

    if not skip_confirm and not confirm("Proceed with uninstall?"):
        print_info("Uninstall cancelled")
        raise typer.Exit(0)

    _run_uninstallation(packages_to_remove, clean, dry_run, state_manager)


@app.command()
def reset(
    ctx: typer.Context,
    confirm_flag: Annotated[
        bool,
        typer.Option("--confirm", help="Confirm reset without prompting"),
    ] = False,
) -> None:
    """Reset: uninstall all tracked packages."""
    dry_run = ctx.obj.get("dry_run", False)

    state_manager = StateManager()
    all_packages = state_manager.get_mac_setup_packages()

    if not all_packages:
        print_info("No mac-setup installed packages to reset")
        raise typer.Exit(0)

    print_uninstall_plan(all_packages, clean=False, dry_run=dry_run)

    if not confirm_flag and not confirm("This will uninstall all packages installed via mac-setup. Continue?", default=False):
        print_info("Reset cancelled")
        raise typer.Exit(0)

    _run_uninstallation(all_packages, clean=False, dry_run=dry_run, state_manager=state_manager)


def _run_installation(
    packages: list[Package],
    dry_run: bool = False,
    skip_confirm: bool = False,
) -> None:
    """Run package installation.

    Args:
        packages: Packages to install
        dry_run: Whether this is a dry run
        skip_confirm: Whether to skip confirmation
    """
    if not packages:
        print_warning("No packages to install")
        return

    # Check Homebrew
    homebrew = HomebrewInstaller()
    if not homebrew.is_available():
        print_error("Homebrew is not installed. Please install it first:")
        console.print('  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        return

    # Filter already installed
    installed_ids = set(homebrew.list_installed())
    to_install = [p for p in packages if p.id not in installed_ids]

    if not to_install:
        print_info("All packages are already installed")
        return

    # Show plan
    print_install_plan(to_install, dry_run=dry_run)

    if dry_run:
        print_info("Dry run - no changes made")
        return

    if not skip_confirm and not confirm(f"Install {len(to_install)} packages?"):
        print_info("Installation cancelled")
        return

    # Install
    state_manager = StateManager()
    results: list[InstallResult] = []
    start_time = time.time()

    with install_progress(len(to_install)) as progress:
        for pkg in to_install:
            progress.update(pkg.name)

            installer = get_installer(pkg.method)

            if pkg.method == InstallMethod.MAS:
                # MAS installation
                from mac_setup.installers.mas import MASInstaller
                mas_installer = MASInstaller()
                result = mas_installer.install(pkg.id, mas_id=pkg.mas_id, dry_run=dry_run)
            else:
                # Homebrew installation
                result = homebrew.install(pkg.id, pkg.method, dry_run=dry_run)

            results.append(result)
            progress.complete_package(result)

            # Track successful installs
            if result.status == InstallStatus.SUCCESS:
                state_manager.add_installed_package(pkg, InstallSource.MAC_SETUP, result.version)

    elapsed = time.time() - start_time
    print_summary(results, "Installation", elapsed)


def _run_uninstallation(
    packages: list,
    clean: bool,
    dry_run: bool,
    state_manager: StateManager,
) -> None:
    """Run package uninstallation."""
    if not packages:
        print_warning("No packages to uninstall")
        return

    homebrew = HomebrewInstaller()
    if not homebrew.is_available():
        print_error("Homebrew is not installed")
        return

    if dry_run:
        print_info("Dry run - no changes made")
        return

    results: list[InstallResult] = []
    start_time = time.time()

    with uninstall_progress(len(packages)) as progress:
        for pkg in packages:
            progress.update(pkg.name)

            if pkg.method == InstallMethod.MAS:
                # MAS uninstall not supported
                result = InstallResult(
                    package_id=pkg.id,
                    status=InstallStatus.FAILED,
                    message="App Store apps must be uninstalled manually",
                )
            else:
                result = homebrew.uninstall(pkg.id, pkg.method, dry_run=dry_run, clean=clean)

            results.append(result)
            progress.complete_package(result, cleaned=clean)

            # Remove from state if successful
            if result.status == InstallStatus.SUCCESS:
                state_manager.remove_installed_package(pkg.id)

    elapsed = time.time() - start_time
    print_summary(results, "Uninstall", elapsed)


if __name__ == "__main__":
    app()
