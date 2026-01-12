"""Tests for utility modules."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from mac_setup.utils.logging import (
    cleanup_old_logs,
    get_logger,
    log_install,
    log_uninstall,
    setup_logging,
)
from mac_setup.utils.subprocess import CommandResult, command_exists, run_command


class TestCommandResult:
    """Tests for CommandResult dataclass."""

    def test_success_when_returncode_zero(self) -> None:
        """Test success property when returncode is 0."""
        result = CommandResult(
            command="echo hello",
            returncode=0,
            stdout="hello",
            stderr="",
        )
        assert result.success is True

    def test_failure_when_returncode_nonzero(self) -> None:
        """Test success property when returncode is non-zero."""
        result = CommandResult(
            command="false",
            returncode=1,
            stdout="",
            stderr="error",
        )
        assert result.success is False

    def test_failure_when_timed_out(self) -> None:
        """Test success property when timed out."""
        result = CommandResult(
            command="sleep 100",
            returncode=0,
            stdout="",
            stderr="",
            timed_out=True,
        )
        assert result.success is False

    def test_default_timed_out_is_false(self) -> None:
        """Test that timed_out defaults to False."""
        result = CommandResult(
            command="test",
            returncode=0,
            stdout="",
            stderr="",
        )
        assert result.timed_out is False


class TestRunCommand:
    """Tests for run_command function."""

    def test_dry_run_returns_mock_result(self) -> None:
        """Test that dry_run mode doesn't execute command."""
        result = run_command(["echo", "hello"], dry_run=True)
        assert result.returncode == 0
        assert "[DRY RUN]" in result.stdout
        assert "echo hello" in result.stdout

    @patch("mac_setup.utils.subprocess.subprocess.run")
    def test_successful_command(self, mock_run: MagicMock) -> None:
        """Test successful command execution."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="output",
            stderr="",
        )
        result = run_command(["echo", "test"])
        assert result.success is True
        assert result.stdout == "output"

    @patch("mac_setup.utils.subprocess.subprocess.run")
    def test_failed_command(self, mock_run: MagicMock) -> None:
        """Test failed command execution."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error message",
        )
        result = run_command(["false"])
        assert result.success is False
        assert result.returncode == 1

    @patch("mac_setup.utils.subprocess.subprocess.run")
    def test_timeout_handling(self, mock_run: MagicMock) -> None:
        """Test timeout handling."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="sleep", timeout=1)
        result = run_command(["sleep", "100"], timeout=1)
        assert result.success is False
        assert result.timed_out is True
        assert "timed out" in result.stderr

    @patch("mac_setup.utils.subprocess.subprocess.run")
    def test_command_not_found(self, mock_run: MagicMock) -> None:
        """Test handling of missing command."""
        mock_run.side_effect = FileNotFoundError()
        result = run_command(["nonexistent_command"])
        assert result.success is False
        assert result.returncode == -1
        assert "not found" in result.stderr.lower()

    @patch("mac_setup.utils.subprocess.subprocess.run")
    def test_subprocess_error(self, mock_run: MagicMock) -> None:
        """Test handling of subprocess errors."""
        import subprocess

        mock_run.side_effect = subprocess.SubprocessError("Some error")
        result = run_command(["bad_command"])
        assert result.success is False
        assert result.returncode == -1

    @patch("mac_setup.utils.subprocess.subprocess.run")
    def test_capture_output_disabled(self, mock_run: MagicMock) -> None:
        """Test with capture_output disabled."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=None,
            stderr=None,
        )
        result = run_command(["echo", "test"], capture_output=False)
        assert result.stdout == ""
        assert result.stderr == ""

    @patch("mac_setup.utils.subprocess.subprocess.run")
    def test_cwd_parameter(self, mock_run: MagicMock) -> None:
        """Test working directory parameter."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        run_command(["ls"], cwd="/tmp")
        mock_run.assert_called_once()
        assert mock_run.call_args.kwargs["cwd"] == "/tmp"


class TestCommandExists:
    """Tests for command_exists function."""

    def test_existing_command(self) -> None:
        """Test that existing commands are found."""
        # 'ls' should exist on all Unix systems
        assert command_exists("ls") is True

    def test_nonexistent_command(self) -> None:
        """Test that nonexistent commands are not found."""
        assert command_exists("nonexistent_command_xyz123") is False


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_default_logging(self, temp_config_dir: Path) -> None:
        """Test default logging setup."""
        logger = setup_logging(log_to_file=False)
        assert logger.name == "mac-setup"
        assert logger.level == logging.DEBUG

    def test_verbose_logging(self, temp_config_dir: Path) -> None:
        """Test verbose logging enables DEBUG level on console."""
        logger = setup_logging(verbose=True, log_to_file=False)
        # Check that console handler has DEBUG level
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.level == logging.DEBUG

    def test_quiet_logging(self, temp_config_dir: Path) -> None:
        """Test quiet logging enables ERROR level on console."""
        logger = setup_logging(quiet=True, log_to_file=False)
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.level == logging.ERROR

    def test_file_logging(self, temp_config_dir: Path) -> None:
        """Test file logging creates log file."""
        with patch("mac_setup.utils.logging.LOGS_DIR", temp_config_dir / "logs"):
            (temp_config_dir / "logs").mkdir(parents=True, exist_ok=True)
            logger = setup_logging(log_to_file=True)
            assert len(logger.handlers) == 2  # console + file


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_creates_logger(self, temp_config_dir: Path) -> None:
        """Test that get_logger creates a logger if none exists."""
        # Reset the global logger
        import mac_setup.utils.logging as log_module

        log_module._logger = None
        with patch.object(log_module, "setup_logging") as mock_setup:
            mock_setup.return_value = logging.getLogger("test")
            get_logger()
            mock_setup.assert_called_once()

    def test_get_logger_returns_existing(self, temp_config_dir: Path) -> None:
        """Test that get_logger returns existing logger."""
        import mac_setup.utils.logging as log_module

        test_logger = logging.getLogger("test-existing")
        log_module._logger = test_logger
        result = get_logger()
        assert result is test_logger


class TestLogInstall:
    """Tests for log_install function."""

    def test_log_install_success(self, temp_config_dir: Path) -> None:
        """Test logging successful installation."""
        with patch("mac_setup.utils.logging.get_logger") as mock_get:
            mock_logger = MagicMock()
            mock_get.return_value = mock_logger
            log_install("test-pkg", success=True, message="v1.0")
            mock_logger.info.assert_called_once()
            assert "test-pkg" in mock_logger.info.call_args[0][0]

    def test_log_install_failure(self, temp_config_dir: Path) -> None:
        """Test logging failed installation."""
        with patch("mac_setup.utils.logging.get_logger") as mock_get:
            mock_logger = MagicMock()
            mock_get.return_value = mock_logger
            log_install("test-pkg", success=False, message="error")
            mock_logger.error.assert_called_once()


class TestLogUninstall:
    """Tests for log_uninstall function."""

    def test_log_uninstall_success(self, temp_config_dir: Path) -> None:
        """Test logging successful uninstall."""
        with patch("mac_setup.utils.logging.get_logger") as mock_get:
            mock_logger = MagicMock()
            mock_get.return_value = mock_logger
            log_uninstall("test-pkg", success=True)
            mock_logger.info.assert_called_once()

    def test_log_uninstall_failure(self, temp_config_dir: Path) -> None:
        """Test logging failed uninstall."""
        with patch("mac_setup.utils.logging.get_logger") as mock_get:
            mock_logger = MagicMock()
            mock_get.return_value = mock_logger
            log_uninstall("test-pkg", success=False, message="error")
            mock_logger.error.assert_called_once()


class TestCleanupOldLogs:
    """Tests for cleanup_old_logs function."""

    def test_cleanup_nonexistent_dir(self, temp_config_dir: Path) -> None:
        """Test cleanup when logs directory doesn't exist."""
        with patch("mac_setup.utils.logging.LOGS_DIR", temp_config_dir / "nonexistent"):
            removed = cleanup_old_logs()
            assert removed == 0

    def test_cleanup_removes_old_files(self, temp_config_dir: Path) -> None:
        """Test cleanup removes old log files."""
        import os
        logs_dir = temp_config_dir / "logs"
        logs_dir.mkdir(parents=True)

        # Create old log file
        old_log = logs_dir / "mac-setup-old.log"
        old_log.write_text("old log content")

        # Set the file's mtime to 60 days ago
        old_time = (datetime.now() - timedelta(days=60)).timestamp()
        os.utime(old_log, (old_time, old_time))

        with patch("mac_setup.utils.logging.LOGS_DIR", logs_dir):
            removed = cleanup_old_logs(keep_days=30)
            # File should be removed
            assert removed == 1
            assert not old_log.exists()

    def test_cleanup_keeps_recent_files(self, temp_config_dir: Path) -> None:
        """Test cleanup keeps recent log files."""
        logs_dir = temp_config_dir / "logs"
        logs_dir.mkdir(parents=True)

        # Create recent log file
        recent_log = logs_dir / "mac-setup-recent.log"
        recent_log.write_text("recent log content")

        with patch("mac_setup.utils.logging.LOGS_DIR", logs_dir):
            cleanup_old_logs(keep_days=30)
            assert recent_log.exists()  # Should still exist
