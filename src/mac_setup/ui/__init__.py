"""UI components for mac-setup."""

from mac_setup.ui.display import (
    print_banner,
    print_category_table,
    print_error,
    print_info,
    print_package_table,
    print_success,
    print_summary,
    print_warning,
)
from mac_setup.ui.progress import InstallProgress
from mac_setup.ui.prompts import (
    confirm,
    prompt_category_selection,
    prompt_main_menu,
    prompt_package_selection,
    prompt_preset_name,
    prompt_uninstall_mode,
)

__all__ = [
    # Display
    "print_banner",
    "print_category_table",
    "print_error",
    "print_info",
    "print_package_table",
    "print_success",
    "print_summary",
    "print_warning",
    # Progress
    "InstallProgress",
    # Prompts
    "confirm",
    "prompt_category_selection",
    "prompt_main_menu",
    "prompt_package_selection",
    "prompt_preset_name",
    "prompt_uninstall_mode",
]
