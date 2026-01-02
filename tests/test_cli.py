"""Tests for CLI module."""

import pytest

from pykellymotion.cli import create_parser


class TestCLIParser:
    """Tests for CLI argument parsing."""

    def test_parser_creation(self):
        """Test parser can be created."""
        parser = create_parser()
        assert parser is not None

    def test_parser_port_required(self):
        """Test port argument is required."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parser_port_only(self):
        """Test parsing with port only (defaults to monitor)."""
        parser = create_parser()
        args = parser.parse_args(["COM3"])

        assert args.port == "COM3"
        assert args.command is None  # Will default to monitor in main()
        assert args.debug is False

    def test_parser_debug_flag(self):
        """Test debug flag."""
        parser = create_parser()
        args = parser.parse_args(["COM3", "--debug"])

        assert args.debug is True

    def test_parser_monitor_command(self):
        """Test monitor command with interval."""
        parser = create_parser()
        args = parser.parse_args(["COM3", "monitor", "--interval", "0.25"])

        assert args.command == "monitor"
        assert args.interval == 0.25

    def test_parser_config_command(self):
        """Test config command with raw flag."""
        parser = create_parser()
        args = parser.parse_args(["COM3", "config", "--raw"])

        assert args.command == "config"
        assert args.raw is True

    def test_parser_single_json(self):
        """Test single command with JSON output."""
        parser = create_parser()
        args = parser.parse_args(["COM3", "single", "--json"])

        assert args.command == "single"
        assert args.json is True

    def test_parser_version_command(self):
        """Test version command."""
        parser = create_parser()
        args = parser.parse_args(["COM3", "version"])

        assert args.command == "version"

    def test_parser_linux_port(self):
        """Test with Linux-style port."""
        parser = create_parser()
        args = parser.parse_args(["/dev/ttyUSB0", "monitor"])

        assert args.port == "/dev/ttyUSB0"
