"""Package catalog with all available categories and packages."""

from mac_setup.models import Category, InstallMethod, Package

# =============================================================================
# Browsers
# =============================================================================
BROWSERS = Category(
    id="browsers",
    name="Browsers",
    description="Web browsers for daily use",
    icon="🌐",
    packages=[
        Package(
            id="google-chrome",
            name="Google Chrome",
            description="Fast, popular, great DevTools",
            method=InstallMethod.CASK,
            app_name="Google Chrome",
            default=True,
        ),
        Package(
            id="firefox",
            name="Firefox",
            description="Privacy-focused, open source",
            method=InstallMethod.CASK,
            app_name="Firefox",
        ),
        Package(
            id="brave-browser",
            name="Brave",
            description="Privacy browser with ad blocking",
            method=InstallMethod.CASK,
            app_name="Brave Browser",
        ),
        Package(
            id="arc",
            name="Arc",
            description="Modern browser with spaces/tabs",
            method=InstallMethod.CASK,
            app_name="Arc",
        ),
        Package(
            id="zen-browser",
            name="Zen",
            description="Firefox-based, minimal UI",
            method=InstallMethod.CASK,
            app_name="Zen Browser",
        ),
        Package(
            id="orion",
            name="Orion",
            description="WebKit browser with extension support",
            method=InstallMethod.CASK,
            app_name="Orion",
        ),
    ],
)

# =============================================================================
# IDEs & Code Editors
# =============================================================================
EDITORS = Category(
    id="editors",
    name="IDEs & Code Editors",
    description="Code editors and development environments",
    icon="📝",
    packages=[
        Package(
            id="visual-studio-code",
            name="VS Code",
            description="Popular, extensible editor",
            method=InstallMethod.CASK,
            app_name="Visual Studio Code",
            default=True,
        ),
        Package(
            id="cursor",
            name="Cursor",
            description="AI-native code editor",
            method=InstallMethod.CASK,
            app_name="Cursor",
        ),
        Package(
            id="zed",
            name="Zed",
            description="Fast, collaborative editor",
            method=InstallMethod.CASK,
            app_name="Zed",
        ),
        Package(
            id="jetbrains-toolbox",
            name="JetBrains Toolbox",
            description="Manage IntelliJ, PyCharm, etc.",
            method=InstallMethod.CASK,
            app_name="JetBrains Toolbox",
        ),
    ],
)

# =============================================================================
# Terminals
# =============================================================================
TERMINALS = Category(
    id="terminals",
    name="Terminals",
    description="Terminal emulators",
    icon="💻",
    packages=[
        Package(
            id="iterm2",
            name="iTerm2",
            description="Classic macOS terminal",
            method=InstallMethod.CASK,
            app_name="iTerm",
            default=True,
        ),
        Package(
            id="wezterm",
            name="WezTerm",
            description="GPU-accelerated, Lua config",
            method=InstallMethod.CASK,
            app_name="WezTerm",
        ),
        Package(
            id="alacritty",
            name="Alacritty",
            description="Minimal, fast terminal",
            method=InstallMethod.CASK,
            app_name="Alacritty",
        ),
        Package(
            id="kitty",
            name="Kitty",
            description="Feature-rich GPU terminal",
            method=InstallMethod.CASK,
            app_name="kitty",
        ),
        Package(
            id="warp",
            name="Warp",
            description="AI-powered modern terminal",
            method=InstallMethod.CASK,
            app_name="Warp",
        ),
        Package(
            id="ghostty",
            name="Ghostty",
            description="Native, fast terminal",
            method=InstallMethod.CASK,
            app_name="Ghostty",
        ),
    ],
)

# =============================================================================
# Shells & Prompts
# =============================================================================
SHELLS = Category(
    id="shells",
    name="Shells & Prompts",
    description="Shells and prompt customization",
    icon="🐚",
    packages=[
        Package(
            id="zsh",
            name="Zsh",
            description="Default macOS shell (extended)",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="fish",
            name="Fish",
            description="User-friendly shell",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="starship",
            name="Starship",
            description="Cross-shell prompt",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="oh-my-posh",
            name="Oh My Posh",
            description="Prompt theme engine",
            method=InstallMethod.FORMULA,
        ),
    ],
)

# =============================================================================
# CLI Utilities
# =============================================================================
CLI_UTILITIES = Category(
    id="cli",
    name="CLI Utilities",
    description="Command-line tools and utilities",
    icon="⌨️",
    packages=[
        Package(
            id="git",
            name="Git",
            description="Version control",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="gh",
            name="GitHub CLI",
            description="GitHub from terminal",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="ripgrep",
            name="ripgrep",
            description="Fast recursive search",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="fd",
            name="fd",
            description="Fast file finder",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="bat",
            name="bat",
            description="Cat with syntax highlighting",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="fzf",
            name="fzf",
            description="Fuzzy finder",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="jq",
            name="jq",
            description="JSON processor",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="yq",
            name="yq",
            description="YAML processor",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="eza",
            name="eza",
            description="Modern ls replacement",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="htop",
            name="htop",
            description="Interactive process viewer",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="btop",
            name="btop",
            description="Resource monitor",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="tldr",
            name="tldr",
            description="Simplified man pages",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="zoxide",
            name="zoxide",
            description="Smarter cd command",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="direnv",
            name="direnv",
            description="Per-directory env vars",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="tmux",
            name="tmux",
            description="Terminal multiplexer",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="neovim",
            name="Neovim",
            description="Modern vim editor",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="wget",
            name="wget",
            description="File downloader",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="delta",
            name="delta",
            description="Better git diff viewer",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="dust",
            name="dust",
            description="Modern du replacement",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="procs",
            name="procs",
            description="Modern ps replacement",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="hyperfine",
            name="hyperfine",
            description="CLI benchmarking tool",
            method=InstallMethod.FORMULA,
        ),
    ],
)

# =============================================================================
# Development Tools
# =============================================================================
DEV_TOOLS = Category(
    id="dev_tools",
    name="Development Tools",
    description="Tools for software development",
    icon="🔧",
    packages=[
        Package(
            id="docker",
            name="Docker Desktop",
            description="Containerization",
            method=InstallMethod.CASK,
            app_name="Docker",
        ),
        Package(
            id="orbstack",
            name="OrbStack",
            description="Fast Docker/Linux on Mac",
            method=InstallMethod.CASK,
            app_name="OrbStack",
        ),
        Package(
            id="postman",
            name="Postman",
            description="API development platform",
            method=InstallMethod.CASK,
            app_name="Postman",
        ),
        Package(
            id="insomnia",
            name="Insomnia",
            description="API client",
            method=InstallMethod.CASK,
            app_name="Insomnia",
        ),
        Package(
            id="httpie",
            name="HTTPie",
            description="User-friendly HTTP client",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="ngrok",
            name="ngrok",
            description="Secure tunnels",
            method=InstallMethod.CASK,
            app_name="ngrok",
        ),
        Package(
            id="lazygit",
            name="LazyGit",
            description="Terminal UI for git",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="lazydocker",
            name="LazyDocker",
            description="Terminal UI for docker",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="sourcetree",
            name="Sourcetree",
            description="Free Git GUI by Atlassian",
            method=InstallMethod.CASK,
            app_name="Sourcetree",
        ),
        Package(
            id="bruno",
            name="Bruno",
            description="Open-source API client",
            method=InstallMethod.CASK,
            app_name="Bruno",
        ),
    ],
)

# =============================================================================
# Languages & Runtimes
# =============================================================================
LANGUAGES = Category(
    id="languages",
    name="Languages & Runtimes",
    description="Programming languages and runtimes",
    icon="🗣️",
    packages=[
        Package(
            id="python@3.12",
            name="Python 3.12",
            description="Python runtime",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="node",
            name="Node.js",
            description="JavaScript runtime",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="deno",
            name="Deno",
            description="JavaScript runtime",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="bun",
            name="Bun",
            description="Fast JS runtime & toolkit",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="go",
            name="Go",
            description="Go programming language",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="rust",
            name="Rust",
            description="Rust via rustup",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="ruby",
            name="Ruby",
            description="Ruby runtime",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="openjdk",
            name="OpenJDK",
            description="Java development kit",
            method=InstallMethod.FORMULA,
        ),
    ],
)

# =============================================================================
# Package & Version Managers
# =============================================================================
PACKAGE_MANAGERS = Category(
    id="package_managers",
    name="Package & Version Managers",
    description="Package and version management tools",
    icon="📦",
    packages=[
        Package(
            id="uv",
            name="uv",
            description="Fast Python package manager",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="pipx",
            name="pipx",
            description="Install Python CLI tools in isolation",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="pnpm",
            name="pnpm",
            description="Fast, disk-efficient package manager",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="yarn",
            name="Yarn",
            description="Alternative npm client",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="mise",
            name="mise",
            description="Universal version manager",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="nvm",
            name="nvm",
            description="Node Version Manager",
            method=InstallMethod.FORMULA,
        ),
    ],
)

# =============================================================================
# Coding Agents
# =============================================================================
CODING_AGENTS = Category(
    id="coding_agents",
    name="Coding Agents",
    description="AI-powered coding assistants",
    icon="🤖",
    packages=[
        Package(
            id="claude-code",
            name="Claude Code",
            description="Anthropic's AI coding assistant CLI",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="codex",
            name="Codex",
            description="OpenAI's CLI coding assistant",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="gemini-cli",
            name="Gemini CLI",
            description="Google's AI assistant CLI",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="opencode",
            name="opencode",
            description="Open source AI coding assistant",
            method=InstallMethod.FORMULA,
        ),
    ],
)

# =============================================================================
# Databases & Data Tools
# =============================================================================
DATABASES = Category(
    id="databases",
    name="Databases & Data Tools",
    description="Databases and data management tools",
    icon="🗃️",
    packages=[
        Package(
            id="sqlite",
            name="SQLite",
            description="Embedded database",
            method=InstallMethod.FORMULA,
            default=True,
        ),
        Package(
            id="postgresql@16",
            name="PostgreSQL",
            description="Relational database",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="mysql",
            name="MySQL",
            description="Relational database",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="redis",
            name="Redis",
            description="In-memory data store",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="mongodb-community",
            name="MongoDB",
            description="Document database",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="dbeaver-community",
            name="DBeaver",
            description="Universal DB client",
            method=InstallMethod.CASK,
            app_name="DBeaver",
        ),
    ],
)

# =============================================================================
# Productivity
# =============================================================================
PRODUCTIVITY = Category(
    id="productivity",
    name="Productivity",
    description="Productivity and utility apps",
    icon="⚡",
    packages=[
        Package(
            id="hiddenbar",
            name="Hidden Bar",
            description="Hide menu bar icons",
            method=InstallMethod.CASK,
            app_name="Hidden Bar",
            default=True,
        ),
        Package(
            id="maccy",
            name="Maccy",
            description="Clipboard manager",
            method=InstallMethod.CASK,
            app_name="Maccy",
            default=True,
        ),
        Package(
            id="raycast",
            name="Raycast",
            description="Launcher & productivity tool",
            method=InstallMethod.CASK,
            app_name="Raycast",
        ),
        Package(
            id="alfred",
            name="Alfred",
            description="Powerful launcher",
            method=InstallMethod.CASK,
            app_name="Alfred 5",
        ),
        Package(
            id="notion",
            name="Notion",
            description="Notes & workspace",
            method=InstallMethod.CASK,
            app_name="Notion",
        ),
        Package(
            id="obsidian",
            name="Obsidian",
            description="Markdown knowledge base",
            method=InstallMethod.CASK,
            app_name="Obsidian",
        ),
        Package(
            id="affine",
            name="Affine",
            description="Open source Markdown knowledge base",
            method=InstallMethod.CASK,
            app_name="AFFiNE",
        ),
        Package(
            id="bitwarden",
            name="Bitwarden",
            description="Open source password manager",
            method=InstallMethod.CASK,
            app_name="Bitwarden",
        ),
        Package(
            id="rectangle",
            name="Rectangle",
            description="Window management",
            method=InstallMethod.CASK,
            app_name="Rectangle",
        ),
        Package(
            id="alt-tab",
            name="AltTab",
            description="Windows-style alt-tab",
            method=InstallMethod.CASK,
            app_name="AltTab",
        ),
        Package(
            id="meetingbar",
            name="MeetingBar",
            description="Calendar in menu bar",
            method=InstallMethod.CASK,
            app_name="MeetingBar",
        ),
        Package(
            id="shottr",
            name="Shottr",
            description="Free screenshot tool with annotations",
            method=InstallMethod.CASK,
            app_name="Shottr",
        ),
        Package(
            id="amphetamine",
            name="Amphetamine",
            description="Keep Mac awake",
            method=InstallMethod.MAS,
            mas_id=937984704,
        ),
    ],
)

# =============================================================================
# Communication
# =============================================================================
COMMUNICATION = Category(
    id="communication",
    name="Communication",
    description="Communication and messaging apps",
    icon="💬",
    packages=[
        Package(
            id="slack",
            name="Slack",
            description="Team messaging",
            method=InstallMethod.CASK,
            app_name="Slack",
        ),
        Package(
            id="discord",
            name="Discord",
            description="Community chat",
            method=InstallMethod.CASK,
            app_name="Discord",
        ),
        Package(
            id="zoom",
            name="Zoom",
            description="Video conferencing",
            method=InstallMethod.CASK,
            app_name="zoom.us",
        ),
        Package(
            id="microsoft-teams",
            name="Microsoft Teams",
            description="Enterprise communication",
            method=InstallMethod.CASK,
            app_name="Microsoft Teams",
        ),
        Package(
            id="telegram",
            name="Telegram",
            description="Messaging app",
            method=InstallMethod.CASK,
            app_name="Telegram",
        ),
        Package(
            id="signal",
            name="Signal",
            description="Private messaging",
            method=InstallMethod.CASK,
            app_name="Signal",
        ),
        Package(
            id="whatsapp",
            name="WhatsApp",
            description="Popular messenger",
            method=InstallMethod.CASK,
            app_name="WhatsApp",
        ),
    ],
)

# =============================================================================
# Design & Creative
# =============================================================================
CREATIVE = Category(
    id="creative",
    name="Design & Creative",
    description="Design, media, and creative tools",
    icon="🎨",
    packages=[
        Package(
            id="vlc",
            name="VLC",
            description="Media player",
            method=InstallMethod.CASK,
            app_name="VLC",
            default=True,
        ),
        Package(
            id="figma",
            name="Figma",
            description="Collaborative design",
            method=InstallMethod.CASK,
            app_name="Figma",
        ),
        Package(
            id="imageoptim",
            name="ImageOptim",
            description="Image compression",
            method=InstallMethod.CASK,
            app_name="ImageOptim",
        ),
        Package(
            id="handbrake",
            name="HandBrake",
            description="Video transcoder",
            method=InstallMethod.CASK,
            app_name="HandBrake",
        ),
        Package(
            id="obs",
            name="OBS Studio",
            description="Streaming/recording",
            method=InstallMethod.CASK,
            app_name="OBS",
        ),
        Package(
            id="iina",
            name="IINA",
            description="Modern media player",
            method=InstallMethod.CASK,
            app_name="IINA",
        ),
        Package(
            id="spotify",
            name="Spotify",
            description="Music streaming",
            method=InstallMethod.CASK,
            app_name="Spotify",
        ),
        Package(
            id="davinci-resolve",
            name="DaVinci Resolve",
            description="Free professional video editor",
            method=InstallMethod.CASK,
            app_name="DaVinci Resolve",
        ),
    ],
)

# =============================================================================
# Cloud & DevOps
# =============================================================================
CLOUD_DEVOPS = Category(
    id="cloud_devops",
    name="Cloud & DevOps",
    description="Cloud CLI tools and DevOps utilities",
    icon="☁️",
    packages=[
        Package(
            id="awscli",
            name="AWS CLI",
            description="Amazon Web Services CLI",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="google-cloud-sdk",
            name="Google Cloud SDK",
            description="GCP CLI tools",
            method=InstallMethod.CASK,
            app_name="Google Cloud SDK",
        ),
        Package(
            id="azure-cli",
            name="Azure CLI",
            description="Microsoft Azure CLI",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="terraform",
            name="Terraform",
            description="Infrastructure as code",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="kubectl",
            name="kubectl",
            description="Kubernetes CLI",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="helm",
            name="Helm",
            description="Kubernetes package manager",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="k9s",
            name="K9s",
            description="Kubernetes TUI",
            method=InstallMethod.FORMULA,
        ),
    ],
)

# =============================================================================
# Virtualization
# =============================================================================
VIRTUALIZATION = Category(
    id="virtualization",
    name="Virtualization",
    description="Virtual machine and container tools",
    icon="🖥️",
    packages=[
        Package(
            id="utm",
            name="UTM",
            description="macOS virtualization",
            method=InstallMethod.CASK,
            app_name="UTM",
        ),
    ],
)

# =============================================================================
# Writing & Documents
# =============================================================================
WRITING = Category(
    id="writing",
    name="Writing & Documents",
    description="Document and writing tools",
    icon="✍️",
    packages=[
        Package(
            id="pandoc",
            name="Pandoc",
            description="Document converter",
            method=InstallMethod.FORMULA,
        ),
        Package(
            id="texmaker",
            name="Texmaker",
            description="LaTeX editor",
            method=InstallMethod.CASK,
            app_name="Texmaker",
        ),
    ],
)

# =============================================================================
# System Utilities
# =============================================================================
SYSTEM_UTILITIES = Category(
    id="system",
    name="System Utilities",
    description="System maintenance and utility apps",
    icon="🛠️",
    packages=[
        Package(
            id="appcleaner",
            name="AppCleaner",
            description="Clean app uninstalls",
            method=InstallMethod.CASK,
            app_name="AppCleaner",
            default=True,
        ),
        Package(
            id="the-unarchiver",
            name="The Unarchiver",
            description="Archive extraction",
            method=InstallMethod.CASK,
            app_name="The Unarchiver",
            default=True,
        ),
        Package(
            id="keka",
            name="Keka",
            description="File archiver",
            method=InstallMethod.CASK,
            app_name="Keka",
        ),
        Package(
            id="coconutbattery",
            name="CoconutBattery",
            description="Battery health",
            method=InstallMethod.CASK,
            app_name="coconutBattery",
        ),
        Package(
            id="stats",
            name="Stats",
            description="System monitor in menubar",
            method=InstallMethod.CASK,
            app_name="Stats",
        ),
        Package(
            id="karabiner-elements",
            name="Karabiner",
            description="Keyboard customization",
            method=InstallMethod.CASK,
            app_name="Karabiner-Elements",
        ),
        Package(
            id="monitorcontrol",
            name="MonitorControl",
            description="External display brightness",
            method=InstallMethod.CASK,
            app_name="MonitorControl",
        ),
    ],
)

# =============================================================================
# Security
# =============================================================================
SECURITY = Category(
    id="security",
    name="Security",
    description="Security and privacy tools",
    icon="🔒",
    packages=[
        Package(
            id="gpg-suite",
            name="GPG Suite",
            description="GPG encryption tools",
            method=InstallMethod.CASK,
            app_name="GPG Keychain",
        ),
    ],
)

# =============================================================================
# Fonts
# =============================================================================
FONTS = Category(
    id="fonts",
    name="Fonts",
    description="Developer and UI fonts",
    icon="🔤",
    packages=[
        Package(
            id="font-fira-code",
            name="Fira Code",
            description="Monospace with ligatures",
            method=InstallMethod.CASK,
            default=True,
        ),
        Package(
            id="font-jetbrains-mono",
            name="JetBrains Mono",
            description="Developer font",
            method=InstallMethod.CASK,
        ),
        Package(
            id="font-inter",
            name="Inter",
            description="UI typeface",
            method=InstallMethod.CASK,
        ),
        Package(
            id="font-sf-mono",
            name="SF Mono",
            description="Apple's monospace",
            method=InstallMethod.CASK,
        ),
        Package(
            id="font-cascadia-code",
            name="Cascadia Code",
            description="Microsoft's dev font",
            method=InstallMethod.CASK,
        ),
        Package(
            id="font-monaspace",
            name="Monaspace",
            description="GitHub's font superfamily",
            method=InstallMethod.CASK,
        ),
    ],
)


# =============================================================================
# Catalog Functions
# =============================================================================

# All categories in display order
ALL_CATEGORIES: list[Category] = [
    BROWSERS,
    EDITORS,
    TERMINALS,
    SHELLS,
    CLI_UTILITIES,
    DEV_TOOLS,
    LANGUAGES,
    PACKAGE_MANAGERS,
    CODING_AGENTS,
    DATABASES,
    PRODUCTIVITY,
    COMMUNICATION,
    CREATIVE,
    CLOUD_DEVOPS,
    VIRTUALIZATION,
    WRITING,
    SYSTEM_UTILITIES,
    SECURITY,
    FONTS,
]

# Category lookup by ID
_CATEGORY_MAP: dict[str, Category] = {cat.id: cat for cat in ALL_CATEGORIES}

# Package lookup by ID (across all categories)
_PACKAGE_MAP: dict[str, Package] = {}
for category in ALL_CATEGORIES:
    for pkg in category.packages:
        _PACKAGE_MAP[pkg.id] = pkg


def get_all_categories() -> list[Category]:
    """Get all available categories."""
    return ALL_CATEGORIES


def get_category(category_id: str) -> Category | None:
    """Get a category by ID."""
    return _CATEGORY_MAP.get(category_id)


def get_package(package_id: str) -> Package | None:
    """Get a package by ID from any category."""
    return _PACKAGE_MAP.get(package_id)


def get_default_packages() -> list[Package]:
    """Get all packages marked as default across all categories."""
    defaults: list[Package] = []
    for category in ALL_CATEGORIES:
        defaults.extend(category.get_default_packages())
    return defaults


def search_packages(query: str) -> list[Package]:
    """Search packages by name, ID, or description.

    Args:
        query: Search query (case-insensitive)

    Returns:
        List of matching packages
    """
    query_lower = query.lower()
    results: list[Package] = []

    for pkg in _PACKAGE_MAP.values():
        if (
            query_lower in pkg.id.lower()
            or query_lower in pkg.name.lower()
            or query_lower in pkg.description.lower()
        ):
            results.append(pkg)

    return sorted(results, key=lambda p: p.name)


def get_package_category(package_id: str) -> Category | None:
    """Get the category containing a package."""
    for category in ALL_CATEGORIES:
        if category.get_package(package_id):
            return category
    return None


def get_total_package_count() -> int:
    """Get total number of packages in the catalog."""
    return len(_PACKAGE_MAP)


def get_packages_by_method(method: InstallMethod) -> list[Package]:
    """Get all packages with a specific installation method."""
    return [pkg for pkg in _PACKAGE_MAP.values() if pkg.method == method]
