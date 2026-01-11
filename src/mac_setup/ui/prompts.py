"""Interactive prompts using questionary."""

from enum import Enum

import questionary
from questionary import Style

from mac_setup.models import Category, InstalledPackage, Package

# Custom style for prompts
custom_style = Style(
    [
        ("qmark", "fg:ansicyan bold"),
        ("question", "bold"),
        ("answer", "fg:ansicyan"),
        ("pointer", "fg:ansicyan bold"),
        ("highlighted", "fg:ansicyan"),
        ("selected", "fg:ansigreen"),
        ("separator", "fg:ansiwhite"),
        ("instruction", "fg:#888888"),
    ]
)


class MainMenuChoice(str, Enum):
    """Main menu options."""

    FRESH_SETUP = "fresh_setup"
    LOAD_PRESET = "load_preset"
    BROWSE = "browse"
    UPDATE = "update"
    UNINSTALL = "uninstall"
    STATUS = "status"
    EXIT = "exit"


class UninstallMode(str, Enum):
    """Uninstall mode options."""

    STANDARD = "standard"
    CLEAN = "clean"


def prompt_main_menu() -> MainMenuChoice:
    """Display the main menu and get user choice.

    Returns:
        The selected menu option
    """
    choices = [
        questionary.Choice(
            title="Fresh Setup      - Full interactive setup wizard",
            value=MainMenuChoice.FRESH_SETUP,
        ),
        questionary.Choice(
            title="Load Preset      - Install from saved configuration",
            value=MainMenuChoice.LOAD_PRESET,
        ),
        questionary.Choice(
            title="Browse Packages  - Explore categories and packages",
            value=MainMenuChoice.BROWSE,
        ),
        questionary.Choice(
            title="Update Packages  - Update outdated packages",
            value=MainMenuChoice.UPDATE,
        ),
        questionary.Choice(
            title="Uninstall        - Remove installed packages",
            value=MainMenuChoice.UNINSTALL,
        ),
        questionary.Choice(
            title="Check Status     - See what's installed",
            value=MainMenuChoice.STATUS,
        ),
        questionary.Separator(),
        questionary.Choice(
            title="Exit",
            value=MainMenuChoice.EXIT,
        ),
    ]

    result = questionary.select(
        "What would you like to do?",
        choices=choices,
        style=custom_style,
        use_shortcuts=True,
    ).ask()

    return result or MainMenuChoice.EXIT


def prompt_category_selection(
    categories: list[Category],
    preselected: set[str] | None = None,
) -> list[str]:
    """Prompt user to select categories.

    Args:
        categories: List of available categories
        preselected: Set of category IDs to pre-select

    Returns:
        List of selected category IDs
    """
    choices = []
    for cat in categories:
        checked = preselected is None or cat.id in preselected
        choices.append(
            questionary.Choice(
                title=f"{cat.icon} {cat.name} ({len(cat.packages)} packages)",
                value=cat.id,
                checked=checked,
            )
        )

    result = questionary.checkbox(
        "Select categories to browse:",
        choices=choices,
        style=custom_style,
        instruction="(Space to toggle, A to toggle all, I to invert, Enter to confirm)",
    ).ask()

    return result or []


def prompt_package_selection(
    category: Category,
    preselected: set[str] | None = None,
    installed: set[str] | None = None,
) -> list[str]:
    """Prompt user to select packages from a category.

    Args:
        category: The category to select from
        preselected: Set of package IDs to pre-select
        installed: Set of already installed package IDs

    Returns:
        List of selected package IDs
    """
    choices = []
    for pkg in category.packages:
        # Determine if should be checked
        if preselected is not None:
            checked = pkg.id in preselected
        else:
            checked = pkg.default

        # Build title with status indicators
        title = f"{pkg.name} — {pkg.description}"
        if installed and pkg.id in installed:
            title = f"{title} [installed]"

        choices.append(
            questionary.Choice(
                title=title,
                value=pkg.id,
                checked=checked,
            )
        )

    result = questionary.checkbox(
        f"Select packages from {category.name}:",
        choices=choices,
        style=custom_style,
        instruction="(Space to toggle, A to toggle all, I to invert, Enter to confirm)",
    ).ask()

    return result or []


def prompt_packages_to_uninstall(
    packages: list[InstalledPackage],
) -> list[str]:
    """Prompt user to select packages to uninstall.

    Args:
        packages: List of installed packages

    Returns:
        List of selected package IDs
    """
    choices = []
    for pkg in packages:
        choices.append(
            questionary.Choice(
                title=f"{pkg.name} — {pkg.method.value}",
                value=pkg.id,
            )
        )

    result = questionary.checkbox(
        "Select packages to uninstall:",
        choices=choices,
        style=custom_style,
        instruction="(Space to toggle, Enter to confirm)",
    ).ask()

    return result or []


def prompt_packages_to_update(
    packages: list[InstalledPackage],
    available_versions: dict[str, str | None],
) -> list[str]:
    """Prompt user to select packages to update.

    Args:
        packages: List of outdated packages
        available_versions: Dict mapping package_id to available version

    Returns:
        List of selected package IDs
    """
    choices = []
    for pkg in packages:
        installed = pkg.version or "?"
        available = available_versions.get(pkg.id) or "?"
        choices.append(
            questionary.Choice(
                title=f"{pkg.name} — {installed} → {available}",
                value=pkg.id,
                checked=True,  # Pre-select all by default
            )
        )

    result = questionary.checkbox(
        "Select packages to update:",
        choices=choices,
        style=custom_style,
        instruction="(Space to toggle, A=all, I=invert, Enter to confirm)",
    ).ask()

    return result or []


def prompt_preset_selection(presets: list[tuple[str, str]]) -> str | None:
    """Prompt user to select a preset.

    Args:
        presets: List of (name, description) tuples

    Returns:
        Selected preset name, or None if cancelled
    """
    choices = [
        questionary.Choice(
            title=f"{name} — {desc}" if desc else name,
            value=name,
        )
        for name, desc in presets
    ]

    result = questionary.select(
        "Select a preset:",
        choices=choices,
        style=custom_style,
    ).ask()

    return result


def prompt_preset_name() -> str | None:
    """Prompt user to enter a preset name.

    Returns:
        The entered name, or None if cancelled
    """
    result = questionary.text(
        "Enter preset name:",
        style=custom_style,
        validate=lambda text: len(text.strip()) > 0 or "Name cannot be empty",
    ).ask()

    return result.strip() if result else None


def prompt_uninstall_mode() -> UninstallMode:
    """Prompt user to select uninstall mode.

    Returns:
        The selected uninstall mode
    """
    choices = [
        questionary.Choice(
            title="Standard - Remove application only",
            value=UninstallMode.STANDARD,
        ),
        questionary.Choice(
            title="Clean    - Remove app + settings, caches, and data",
            value=UninstallMode.CLEAN,
        ),
    ]

    result = questionary.select(
        "Select uninstall mode:",
        choices=choices,
        style=custom_style,
    ).ask()

    return result or UninstallMode.STANDARD


def confirm(message: str, default: bool = True) -> bool:
    """Ask for confirmation.

    Args:
        message: The confirmation message
        default: Default value if user just presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    result = questionary.confirm(
        message,
        default=default,
        style=custom_style,
    ).ask()

    return result if result is not None else False


def prompt_text(message: str, default: str = "") -> str | None:
    """Prompt for text input.

    Args:
        message: The prompt message
        default: Default value

    Returns:
        The entered text, or None if cancelled
    """
    result = questionary.text(
        message,
        default=default,
        style=custom_style,
    ).ask()

    return result
