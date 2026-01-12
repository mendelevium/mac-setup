"""Subprocess utilities for running shell commands."""

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of a command execution."""

    command: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False

    @property
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.returncode == 0 and not self.timed_out


def run_command(
    args: Sequence[str],
    timeout: int = 120,
    dry_run: bool = False,
    capture_output: bool = True,
    cwd: str | None = None,
) -> CommandResult:
    """Run a shell command with proper error handling.

    Args:
        args: Command and arguments as a sequence
        timeout: Timeout in seconds (default 2 minutes)
        dry_run: If True, don't actually run the command
        capture_output: Whether to capture stdout/stderr
        cwd: Working directory for the command

    Returns:
        CommandResult with the outcome
    """
    command_str = " ".join(args)

    if dry_run:
        return CommandResult(
            command=command_str,
            returncode=0,
            stdout=f"[DRY RUN] Would execute: {command_str}",
            stderr="",
        )

    try:
        result = subprocess.run(
            args,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )

        return CommandResult(
            command=command_str,
            returncode=result.returncode,
            stdout=result.stdout if capture_output else "",
            stderr=result.stderr if capture_output else "",
        )

    except subprocess.TimeoutExpired:
        return CommandResult(
            command=command_str,
            returncode=-1,
            stdout="",
            stderr=f"Command timed out after {timeout} seconds",
            timed_out=True,
        )

    except FileNotFoundError:
        return CommandResult(
            command=command_str,
            returncode=-1,
            stdout="",
            stderr=f"Command not found: {args[0]}",
        )

    except subprocess.SubprocessError as e:
        return CommandResult(
            command=command_str,
            returncode=-1,
            stdout="",
            stderr=str(e),
        )


def command_exists(command: str) -> bool:
    """Check if a command exists in PATH.

    Args:
        command: The command to check

    Returns:
        True if the command exists, False otherwise
    """
    import shutil

    return shutil.which(command) is not None
