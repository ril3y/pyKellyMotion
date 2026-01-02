"""Tests for parser module."""

from pykellymotion.parser import MonitorData, Parser
from pykellymotion.protocol import Commands


class TestMonitorData:
    """Tests for MonitorData dataclass."""

    def test_default_values(self):
        """Test default values are zero."""
        data = MonitorData()

        assert data.tps_pedal == 0
        assert data.motor_speed == 0
        assert data.battery_voltage == 0
        assert data.error_code == 0


class TestParser:
    """Tests for Parser class."""

    def test_init(self):
        """Test parser initialization."""
        parser = Parser()
        assert parser.monitor is not None
        assert parser.debug is False

    def test_parse_monitor_one(self):
        """Test parsing monitor packet 1."""
        parser = Parser()

        # Create test data (16 bytes)
        data = bytes(
            [
                50,  # tps_pedal
                10,  # brake_pedal
                1,  # brake_sw1
                0,  # foot_sw
                1,  # forward_sw
                0,  # reverse_sw
                1,  # hall_a
                0,  # hall_b
                1,  # hall_c
                48,  # battery_voltage
                35,  # motor_temp
                40,  # controller_temp
                1,  # setting_dir
                1,  # actual_dir
                0,  # brake_sw2
                0,  # low_speed
            ]
        )

        result = parser.parse_response(Commands.MONITOR_ONE, data)
        assert result is True

        assert parser.monitor.tps_pedal == 50
        assert parser.monitor.brake_pedal == 10
        assert parser.monitor.forward_sw == 1
        assert parser.monitor.hall_a == 1
        assert parser.monitor.hall_c == 1
        assert parser.monitor.battery_voltage == 48
        assert parser.monitor.motor_temp == 35
        assert parser.monitor.controller_temp == 40

    def test_parse_monitor_two(self):
        """Test parsing monitor packet 2."""
        parser = Parser()

        # Create test data (at least 6 bytes)
        # Motor speed is at offset 3-4 (big-endian), phase current at 5
        data = bytes(
            [
                0x00,
                0x00,
                0x00,  # padding
                0x0B,
                0xB8,  # motor_speed = 3000 RPM (0x0BB8)
                0x32,  # phase_current = 50A
            ]
        )

        result = parser.parse_response(Commands.MONITOR_TWO, data)
        assert result is True

        assert parser.monitor.motor_speed == 3000
        assert parser.monitor.phase_current == 50

    def test_parse_monitor_three(self):
        """Test parsing monitor packet 3."""
        parser = Parser()

        # Error code is first 2 bytes (big-endian)
        data = bytes([0x00, 0x42])  # Error code = 0x0042 (bits 1 and 6)

        result = parser.parse_response(Commands.MONITOR_THREE, data)
        assert result is True

        assert parser.monitor.error_code == 0x0042

    def test_parse_monitor_one_too_short(self):
        """Test parsing fails with insufficient data."""
        parser = Parser()
        data = bytes([0x01, 0x02, 0x03])  # Only 3 bytes, need 16

        result = parser.parse_response(Commands.MONITOR_ONE, data)
        assert result is False

    def test_parse_config(self):
        """Test parsing config data."""
        parser = Parser()
        config_data = bytes([0x01, 0x02, 0x03, 0x04])

        result = parser.parse_response(Commands.READ_CONFIG, config_data)
        assert result is True
        assert parser.config_data == config_data


class TestParserConfigValues:
    """Tests for config value extraction."""

    def test_get_config_value_not_loaded(self):
        """Test getting config value before loading."""
        parser = Parser()
        value = parser.get_config_value("current_percent")
        assert value is None

    def test_get_config_value_unknown_param(self):
        """Test getting unknown parameter."""
        parser = Parser()
        parser._config_data = bytes([0x00] * 100)

        value = parser.get_config_value("nonexistent_param")
        assert value is None

    def test_get_all_config_empty(self):
        """Test getting all config when no data loaded."""
        parser = Parser()
        config = parser.get_all_config()
        assert config == {}
