# mac-setup CLI — Specification

A modern, interactive command-line tool for provisioning new macOS machines with curated software selections.

---

## Overview

**Goal**: Provide a streamlined, opinionated setup experience for new Macs — replacing hours of manual downloads with a single interactive session.

**Philosophy**:
- Curated over comprehensive (quality defaults, not every package)
- Interactive over scripted (guide users through choices)
- Idempotent (safe to re-run anytime)
- Transparent (show what's happening, never surprise the user)

---

## Technical Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | Ubiquitous, good CLI ecosystem |
| CLI Framework | Typer | Modern, type-hinted, auto-generates help |
| Rich Output | Rich | Progress bars, panels, tables, colors |
| Prompts | questionary | Checkbox/select prompts with vim keys |
| Config Format | YAML | Human-readable presets |
| Package Manager | Homebrew | De facto standard for macOS |
| App Store | mas-cli | Automate Mac App Store installs |

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| Category Browser | Navigate software by category with descriptions |
| Multi-select UI | Checkbox interface to pick packages |
| Progress Tracking | Per-package and overall progress bars |
| Preset System | Save/load configurations as YAML files |
| Dry Run Mode | Preview all changes before executing |
| Idempotent Installs | Skip already-installed packages |
| Homebrew Bootstrap | Auto-install Homebrew if missing |
| Uninstall Mode | Remove installed packages with optional clean uninstall |
| Auto-Detection | Scan system for all installed catalog packages (marks mac-setup installs) |

### Nice-to-Have Features

| Feature | Description |
|---------|-------------|
| Dotfiles Integration | Clone and symlink a dotfiles repo |
| Shell Configuration | Set default shell (zsh, fish, bash) |
| macOS Defaults | Apply common system preferences |
| Post-install Hooks | Run custom scripts per-package |
| Update Mode | Update all previously installed packages |
| Export to Script | Generate standalone bash script from preset |

---

## Software Categories & Packages

Each package entry includes:
- `id`: Homebrew formula/cask name
- `name`: Display name
- `description`: One-line description
- `default`: Whether selected by default in interactive mode
- `mas_id`: (optional) Mac App Store ID for mas-cli

### Browsers

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `google-chrome` | Google Chrome | Fast, popular, great DevTools | ✓ |
| `firefox` | Firefox | Privacy-focused, open source | |
| `brave-browser` | Brave | Privacy browser with ad blocking | |
| `arc` | Arc | Modern browser with spaces/tabs | |
| `zen-browser` | Zen | Firefox-based, minimal UI | |
| `orion` | Orion | WebKit browser with extension support | |

### IDEs & Code Editors

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `visual-studio-code` | VS Code | Popular, extensible editor | ✓ |
| `cursor` | Cursor | AI-native code editor | |
| `zed` | Zed | Fast, collaborative editor | |
| `jetbrains-toolbox` | JetBrains Toolbox | Manage IntelliJ, PyCharm, etc. | |

### Terminals

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `iterm2` | iTerm2 | Classic macOS terminal | ✓ |
| `wezterm` | WezTerm | GPU-accelerated, Lua config | |
| `alacritty` | Alacritty | Minimal, fast terminal | |
| `kitty` | Kitty | Feature-rich GPU terminal | |
| `warp` | Warp | AI-powered modern terminal | |
| `ghostty` | Ghostty | Native, fast terminal | |

### Shells & Prompts

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `zsh` | Zsh | Default macOS shell (extended) | ✓ |
| `fish` | Fish | User-friendly shell | |
| `starship` | Starship | Cross-shell prompt | |
| `oh-my-posh` | Oh My Posh | Prompt theme engine | |

### CLI Utilities

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `git` | Git | Version control | ✓ |
| `gh` | GitHub CLI | GitHub from terminal | ✓ |
| `ripgrep` | ripgrep | Fast recursive search | ✓ |
| `fd` | fd | Fast file finder | ✓ |
| `bat` | bat | Cat with syntax highlighting | ✓ |
| `fzf` | fzf | Fuzzy finder | ✓ |
| `jq` | jq | JSON processor | ✓ |
| `yq` | yq | YAML processor | |
| `eza` | eza | Modern ls replacement | |
| `htop` | htop | Interactive process viewer | |
| `btop` | btop | Resource monitor | |
| `tldr` | tldr | Simplified man pages | |
| `zoxide` | zoxide | Smarter cd command | |
| `direnv` | direnv | Per-directory env vars | |
| `tmux` | tmux | Terminal multiplexer | |
| `neovim` | Neovim | Modern vim editor | |
| `wget` | wget | File downloader | |
| `delta` | delta | Better git diff viewer | |
| `dust` | dust | Modern du replacement | |
| `procs` | procs | Modern ps replacement | |
| `hyperfine` | hyperfine | CLI benchmarking tool | |

### Development Tools

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `docker` | Docker Desktop | Containerization | |
| `orbstack` | OrbStack | Fast Docker/Linux on Mac | |
| `postman` | Postman | API development platform | |
| `insomnia` | Insomnia | API client | |
| `httpie` | HTTPie | User-friendly HTTP client | |
| `ngrok` | ngrok | Secure tunnels | |
| `lazygit` | LazyGit | Terminal UI for git | |
| `lazydocker` | LazyDocker | Terminal UI for docker | |
| `sourcetree` | Sourcetree | Free Git GUI by Atlassian | |
| `bruno` | Bruno | Open-source API client | |

### Languages & Runtimes

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `python@3.12` | Python 3.12 | Python runtime | ✓ |
| `node` | Node.js | JavaScript runtime | |
| `deno` | Deno | JavaScript runtime | |
| `bun` | Bun | Fast JS runtime & toolkit | |
| `go` | Go | Go programming language | |
| `rust` | Rust | Rust via rustup | |
| `ruby` | Ruby | Ruby runtime | |
| `java` | OpenJDK | Java development kit | |

### Package & Version Managers

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `uv` | uv | Fast Python package manager | ✓ |
| `pipx` | pipx | Install Python CLI tools in isolation | |
| `npm` | npm | Node.js package manager | |
| `pnpm` | pnpm | Fast, disk-efficient package manager | |
| `yarn` | Yarn | Alternative npm client | |
| `cargo` | Cargo | Rust package manager (via rustup) | |
| `gem` | RubyGems | Ruby package manager | |
| `maven` | Maven | Java build/dependency tool | |
| `gradle` | Gradle | Java/Kotlin build tool | |
| `mise` | mise | Universal version manager | |
| `nvm` | nvm | Node Version Manager | |

### Coding Agents

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `claude-code` | Claude Code | Anthropic's AI coding assistant CLI | ✓ |
| `codex` | Codex | OpenAI's CLI coding assistant | |
| `gemini-cli` | Gemini CLI | Google's AI assistant CLI | |
| `opencode` | opencode | Open source AI coding assistant | |

### Databases & Data Tools

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `sqlite` | SQLite | Embedded database | ✓ |
| `postgresql@16` | PostgreSQL | Relational database | |
| `mysql` | MySQL | Relational database | |
| `redis` | Redis | In-memory data store | |
| `mongodb-community` | MongoDB | Document database | |
| `dbeaver-community` | DBeaver | Universal DB client | |

### Productivity

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `hiddenbar` | Hidden Bar | Hide menu bar icons | ✓ |
| `maccy` | Maccy | Clipboard manager | ✓ |
| `raycast` | Raycast | Launcher & productivity tool | |
| `alfred` | Alfred | Powerful launcher | |
| `notion` | Notion | Notes & workspace | |
| `obsidian` | Obsidian | Markdown knowledge base | |
| `affine` | Affine | Open source Markdown knowledge base | |
| `bitwarden` | Bitwarden | Open source password manager | |
| `rectangle` | Rectangle | Window management | |
| `alt-tab` | AltTab | Windows-style alt-tab | |
| `meetingbar` | MeetingBar | Calendar in menu bar | |
| `shottr` | Shottr | Free screenshot tool with annotations | |
| `amphetamine` | Amphetamine | Keep Mac awake (App Store) | |

### Communication

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `slack` | Slack | Team messaging | |
| `discord` | Discord | Community chat | |
| `zoom` | Zoom | Video conferencing | |
| `microsoft-teams` | Microsoft Teams | Enterprise communication | |
| `telegram` | Telegram | Messaging app | |
| `signal` | Signal | Private messaging | |
| `whatsapp` | WhatsApp | Popular messenger | |

### Design & Creative

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `vlc` | VLC | Media player | ✓ |
| `figma` | Figma | Collaborative design | |
| `imageoptim` | ImageOptim | Image compression | |
| `handbrake` | HandBrake | Video transcoder | |
| `obs` | OBS Studio | Streaming/recording | |
| `iina` | IINA | Modern media player | |
| `spotify` | Spotify | Music streaming | |
| `davinci-resolve` | DaVinci Resolve | Free professional video editor | |

### Cloud & DevOps

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `awscli` | AWS CLI | Amazon Web Services CLI | |
| `google-cloud-sdk` | Google Cloud SDK | GCP CLI tools | |
| `azure-cli` | Azure CLI | Microsoft Azure CLI | |
| `terraform` | Terraform | Infrastructure as code | |
| `docker` | Docker | Lightweight container manager | |
| `kubectl` | kubectl | Kubernetes CLI | |
| `helm` | Helm | Kubernetes package manager | |
| `k9s` | K9s | Kubernetes TUI | |

### Virtualization

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `utm` | UTM | macOS virtualization | |

### Writing & Documents

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `pandoc` | Pandoc | Document converter | |
| `texmaker` | Textmaker | LaTeX editor | |

### System Utilities

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `appcleaner` | AppCleaner | Clean app uninstalls | ✓ |
| `the-unarchiver` | The Unarchiver | Archive extraction | ✓ |
| `keka` | Keka | File archiver | |
| `coconutbattery` | CoconutBattery | Battery health | |
| `stats` | Stats | System monitor in menubar | |
| `karabiner-elements` | Karabiner | Keyboard customization | |
| `monitorcontrol` | MonitorControl | External display brightness | |

### Security

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `gpg-suite` | GPG Suite | GPG encryption tools | |

### Fonts (via Homebrew Cask)

| ID | Name | Description | Default |
|----|------|-------------|---------|
| `font-fira-code` | Fira Code | Monospace with ligatures | ✓ |
| `font-jetbrains-mono` | JetBrains Mono | Developer font | |
| `font-inter` | Inter | UI typeface | |
| `font-sf-mono` | SF Mono | Apple's monospace | |
| `font-cascadia-code` | Cascadia Code | Microsoft's dev font | |
| `font-monaspace` | Monaspace | GitHub's font superfamily | |

---

## Preset Schema

Presets are stored in `~/.config/mac-setup/presets/` as YAML files.

```yaml
# ~/.config/mac-setup/presets/developer.yaml
name: "Developer Workstation"
description: "Full-stack development setup"
version: 1
created: 2025-01-10
author: "Martin"

# Selected packages by category
packages:
  browsers:
    - google-chrome
    - firefox
  editors:
    - visual-studio-code
  terminals:
    - iterm2
  shells:
    - starship
  cli:
    - git
    - gh
    - ripgrep
    - fd
    - bat
    - fzf
    - jq
    - yq
  dev_tools:
    - orbstack
    - httpie
  languages:
    - python@3.12
    - bun
  packages:
    - uv
  databases:
    - postgresql@16
    - sqlite
  productivity:
    - hiddenbar
    - maccy
    - bitwarden
  creative:
    - vlc
  system:
    - appcleaner
    - the-unarchiver
  fonts:
    - font-fira-code

# Optional: Dotfiles repository
dotfiles:
  repo: "git@github.com:username/dotfiles.git"
  method: "stow"  # or "symlink"

# Optional: macOS system preferences
macos_defaults:
  # Dock
  - domain: com.apple.dock
    key: autohide
    type: bool
    value: true
  - domain: com.apple.dock
    key: tilesize
    type: int
    value: 48
  # Finder
  - domain: com.apple.finder
    key: ShowPathbar
    type: bool
    value: true
  - domain: com.apple.finder
    key: AppleShowAllFiles
    type: bool
    value: true
  # Keyboard
  - domain: NSGlobalDomain
    key: KeyRepeat
    type: int
    value: 2
  - domain: NSGlobalDomain
    key: InitialKeyRepeat
    type: int
    value: 15

# Optional: Post-install scripts
post_install:
  - name: "Set Fish as default shell"
    run: |
      echo /opt/homebrew/bin/fish | sudo tee -a /etc/shells
      chsh -s /opt/homebrew/bin/fish
  - name: "Configure Git"
    run: |
      git config --global init.defaultBranch main
      git config --global pull.rebase true
```

---

## CLI Interface

### Commands

```bash
# Interactive setup (full wizard)
mac-setup

# Browse categories and select packages
mac-setup browse

# Install from a preset
mac-setup install --preset developer
mac-setup install --preset ~/my-preset.yaml

# Save current selections to preset
mac-setup save my-setup

# List available presets
mac-setup presets

# Dry run (preview without installing)
mac-setup --dry-run
mac-setup install --preset developer --dry-run

# Update all installed packages
mac-setup update

# Export preset as standalone bash script
mac-setup export --preset developer --output setup.sh

# Check what's already installed
mac-setup status

# Install specific categories only
mac-setup install --category cli,dev_tools

# Reset (uninstall all tracked packages)
mac-setup reset --confirm

# Uninstall packages (interactive selection)
mac-setup uninstall

# Uninstall specific packages
mac-setup uninstall --packages google-chrome,slack

# Clean uninstall (remove settings, caches, app data)
mac-setup uninstall --clean

# Dry run uninstall
mac-setup uninstall --dry-run
```

### Command Options

```bash
Options:
  --dry-run, -n       Preview changes without executing
  --yes, -y           Skip confirmation prompts
  --verbose, -v       Show detailed output
  --quiet, -q         Minimal output
  --no-color          Disable colored output
  --preset, -p FILE   Use preset file
  --category, -c CAT  Filter by category (comma-separated)
  --help, -h          Show help
  --version           Show version

# Uninstall-specific options
  --clean, -c         Remove all associated files (settings, caches, data)
  --packages, -p PKG  Specific packages to uninstall (comma-separated)
```

---

## Interactive UI Flow

### Main Menu

```
╭─────────────────────────────────────────────────────────────╮
│                    🍎 mac-setup v1.0.0                       │
│         Interactive macOS Development Environment          │
╰─────────────────────────────────────────────────────────────╯

? What would you like to do?
❯ ○ Fresh Setup      — Full interactive setup wizard
  ○ Load Preset      — Install from saved configuration
  ○ Browse Packages  — Explore categories and packages
  ○ Uninstall        — Remove installed packages
  ○ Update All       — Update installed packages
  ○ Check Status     — See what's installed
  ○ Exit
```

### Category Browser

```
? Select a category to browse:
❯ ◉ Browsers         (6 packages)
  ◉ IDEs & Editors   (6 packages)  
  ◉ Terminals        (6 packages)
  ○ Shells           (4 packages)
  ◉ CLI Utilities    (15 packages)
  ...

[Press Space to toggle, Enter to select packages, Ctrl+C to cancel]
```

### Package Selection (within category)

```
╭─ IDEs & Code Editors ───────────────────────────────────────╮
│ Select your preferred code editors                          │
╰─────────────────────────────────────────────────────────────╯

? Select packages to install:
  ◉ VS Code          — Popular, extensible editor
❯ ◉ Cursor           — AI-native code editor
  ○ Zed              — Fast, collaborative editor
  ○ Sublime Text     — Lightweight, fast editor
  ○ JetBrains Toolbox— Manage IntelliJ, PyCharm, etc.
  ○ Nova             — Native macOS editor by Panic

[↑↓ Navigate, Space toggle, A select all, N select none, Enter confirm]
```

### Installation Progress

```
╭─ Installing Packages ───────────────────────────────────────╮
│ 12 of 47 packages                                           │
╰─────────────────────────────────────────────────────────────╯

Overall   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  25%  12/47

Currently installing: docker

Completed:
  ✓ google-chrome
  ✓ cursor
  ✓ wezterm  
  ✓ fish
  ✓ starship
  ✓ git
  ✓ gh
  ✓ ripgrep
  ✓ fd
  ✓ bat
  ✓ eza
  ✓ fzf
  ⠋ docker (installing...)

Remaining: 35 packages
```

### Summary Screen

```
╭─ Setup Complete! ───────────────────────────────────────────╮
│                                                             │
│  ✓ 45 packages installed successfully                      │
│  ⚠ 2 packages skipped (already installed)                  │
│  ✗ 0 packages failed                                       │
│                                                             │
│  Time elapsed: 8m 32s                                       │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

? Would you like to save this configuration as a preset?
❯ Yes, save as preset
  No, finish

? Enter preset name: my-dev-setup
✓ Preset saved to ~/.config/mac-setup/presets/my-dev-setup.yaml

Next steps:
  • Restart your terminal to apply shell changes
  • Run 'mac-setup update' periodically to keep packages current
  • Your preset can be reused with: mac-setup install -p my-dev-setup
```

### Uninstall Flow

```
╭─ Uninstall Packages ────────────────────────────────────────╮
│ Select packages to uninstall                                 │
╰─────────────────────────────────────────────────────────────╯

? Select packages to uninstall:
  ◉ google-chrome      — Google Chrome              [mac-setup]
  ○ firefox            — Firefox                    [mac-setup]
❯ ◉ slack              — Slack                      [detected]
  ○ docker             — Docker Desktop             [detected]

[↑↓ Navigate, Space toggle, Enter confirm]

? Select uninstall mode:
❯ ○ Standard    — Remove application only
  ○ Clean       — Remove app + settings, caches, and data
```

**Clean Uninstall Preview:**

```
╭─ Clean Uninstall Preview ───────────────────────────────────╮
│ The following will be removed for "Slack":                   │
│                                                              │
│   /Applications/Slack.app                                    │
│   ~/Library/Application Support/Slack/                       │
│   ~/Library/Preferences/com.tinyspeck.slackmacgap.plist     │
│   ~/Library/Caches/com.tinyspeck.slackmacgap/               │
│                                                              │
│   Total: 245 MB                                              │
╰─────────────────────────────────────────────────────────────╯

? Proceed with uninstall? (y/n)
```

**Uninstall Progress:**

```
╭─ Uninstalling Packages ─────────────────────────────────────╮
│ 2 of 3 packages                                              │
╰─────────────────────────────────────────────────────────────╯

Overall   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  66%  2/3

Completed:
  ✓ google-chrome (cleaned)
  ✓ slack (cleaned)
  ⠋ discord (uninstalling...)
```

**Badge Legend:**
- `[mac-setup]` — Package was installed via mac-setup (tracked in state.json)
- `[detected]` — Package from catalog found on system (installed externally)

---

## Project Structure

```
mac-setup/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── mac-setup/
│       ├── __init__.py
│       ├── cli.py              # Typer app, command definitions
│       ├── config.py           # Settings, paths, constants
│       ├── models.py           # Pydantic models (Package, Preset, etc.)
│       ├── catalog.py          # Package catalog (all categories/packages)
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── prompts.py      # Questionary prompts
│       │   ├── progress.py     # Rich progress bars
│       │   └── display.py      # Rich panels, tables
│       ├── installers/
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract installer
│       │   ├── homebrew.py     # Homebrew (formula + cask)
│       │   └── mas.py          # Mac App Store
│       ├── presets/
│       │   ├── __init__.py
│       │   ├── manager.py      # Save/load/list presets
│       │   └── defaults/       # Built-in presets
│       │       ├── minimal.yaml
│       │       ├── developer.yaml
│       │       └── creative.yaml
│       ├── system/
│       │   ├── __init__.py
│       │   ├── defaults.py     # macOS defaults commands
│       │   ├── dotfiles.py     # Dotfiles cloning/linking
│       │   └── shell.py        # Shell configuration
│       └── utils/
│           ├── __init__.py
│           ├── logging.py      # Structured logging
│           └── subprocess.py   # Command execution wrapper
├── tests/
│   ├── conftest.py
│   ├── test_catalog.py
│   ├── test_installers.py
│   └── test_presets.py
└── docs/
    ├── usage.md
    └── contributing.md
```

---

## Data Models

```python
from enum import Enum
from pydantic import BaseModel

class InstallMethod(str, Enum):
    BREW_FORMULA = "formula"
    BREW_CASK = "cask"
    MAS = "mas"

class Package(BaseModel):
    id: str                          # e.g., "visual-studio-code"
    name: str                        # e.g., "VS Code"
    description: str
    method: InstallMethod = InstallMethod.BREW_CASK
    mas_id: int | None = None        # For App Store apps
    default: bool = False            # Pre-selected in UI
    requires: list[str] = []         # Dependencies
    post_install: str | None = None  # Shell command to run after

class Category(BaseModel):
    id: str                          # e.g., "editors"
    name: str                        # e.g., "IDEs & Code Editors"
    description: str
    icon: str                        # Emoji
    packages: list[Package]

class MacOSDefault(BaseModel):
    domain: str
    key: str
    type: str                        # bool, int, float, string
    value: str | int | float | bool
    description: str | None = None

class Preset(BaseModel):
    name: str
    description: str | None = None
    version: int = 1
    created: str
    author: str | None = None
    packages: dict[str, list[str]]   # category_id -> [package_ids]
    dotfiles: dict | None = None
    macos_defaults: list[MacOSDefault] = []
    post_install: list[dict] = []
```

---

## Error Handling

| Scenario | Handling |
|----------|----------|
| Homebrew not installed | Prompt to install, provide command |
| Package not found | Log warning, continue with others |
| Install fails | Log error, offer retry or skip |
| Network error | Retry with backoff, then fail gracefully |
| Permission denied | Explain what's needed, prompt for sudo |
| Ctrl+C interrupt | Save progress, offer resume option |
| Disk space low | Warn before starting, estimate space needed |
| Package in use (uninstall) | Warn user, offer to force quit or skip |
| Protected system app | Skip with explanation |
| Clean uninstall paths not found | Proceed with standard uninstall |

---

## Configuration Files

| File | Purpose |
|------|---------|
| `~/.config/mac-setup/config.yaml` | User settings |
| `~/.config/mac-setup/presets/` | Saved presets |
| `~/.config/mac-setup/state.json` | Installed packages tracking |
| `~/.config/mac-setup/logs/` | Installation logs |

---

## Future Considerations

- **Cloud sync**: Sync presets via GitHub Gist or iCloud
- **Team presets**: Shared org configurations via URL
- **Plugin system**: Custom package sources
- **GUI wrapper**: Electron/Tauri frontend
- **Ansible export**: Generate Ansible playbook from preset
- **Brewfile compatibility**: Import/export Brewfiles
- **Version pinning**: Lock specific package versions
- **Rollback**: Undo last installation session
