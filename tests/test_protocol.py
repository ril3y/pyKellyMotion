"""Tests for protocol module."""

from pykellymotion.protocol import (
    BAUD_RATE,
    Commands,
    build_packet,
    calculate_checksum,
    decode_errors,
    parse_response,
    validate_response,
)


class TestChecksum:
    """Tests for checksum calculation."""

    def test_calculate_checksum_simple(self):
        """Test checksum with simple data."""
        data = bytes([0x3A, 0x00])
        assert calculate_checksum(data) == 0x3A

    def test_calculate_checksum_with_data(self):
        """Test checksum with data bytes."""
        data = bytes([0x3A, 0x02, 0x01, 0x02])
        expected = (0x3A + 0x02 + 0x01 + 0x02) & 0xFF
        assert calculate_checksum(data) == expected

    def test_calculate_checksum_overflow(self):
        """Test checksum truncation to 8 bits."""
        data = bytes([0xFF, 0xFF, 0xFF])
        assert calculate_checksum(data) == (0xFF * 3) & 0xFF


class TestBuildPacket:
    """Tests for packet building."""

    def test_build_packet_no_data(self):
        """Test packet with no data (checksum = cmd)."""
        packet = build_packet(Commands.MONITOR_ONE)
        assert packet == bytes([0x3A, 0x00, 0x3A])

    def test_build_packet_with_data(self):
        """Test packet with data bytes."""
        data = bytes([0x01, 0x02, 0x03])
        packet = build_packet(0x4C, data)

        assert packet[0] == 0x4C  # cmd
        assert packet[1] == 0x03  # length
        assert packet[2:5] == data  # data
        # checksum = sum of cmd + len + data
        expected_checksum = (0x4C + 0x03 + 0x01 + 0x02 + 0x03) & 0xFF
        assert packet[5] == expected_checksum


class TestValidateResponse:
    """Tests for response validation."""

    def test_validate_response_no_data(self):
        """Test validation of response with no data."""
        # CMD=0x3A, LEN=0, CHECKSUM=0x3A
        packet = bytes([0x3A, 0x00, 0x3A])
        assert validate_response(packet) is True

    def test_validate_response_with_data(self):
        """Test validation of response with data."""
        # Build a valid packet
        cmd = 0x3B
        data = bytes([0x01, 0x02, 0x03, 0x04])
        checksum = (cmd + len(data) + sum(data)) & 0xFF
        packet = bytes([cmd, len(data)]) + data + bytes([checksum])

        assert validate_response(packet) is True

    def test_validate_response_bad_checksum(self):
        """Test rejection of bad checksum."""
        packet = bytes([0x3A, 0x00, 0x00])  # Wrong checksum
        assert validate_response(packet) is False

    def test_validate_response_wrong_cmd(self):
        """Test rejection when expected cmd doesn't match."""
        packet = bytes([0x3A, 0x00, 0x3A])
        assert validate_response(packet, expected_cmd=0x3B) is False

    def test_validate_response_too_short(self):
        """Test rejection of too-short packet."""
        packet = bytes([0x3A, 0x00])  # Missing checksum
        assert validate_response(packet) is False


class TestParseResponse:
    """Tests for response parsing."""

    def test_parse_response_no_data(self):
        """Test parsing response with no data."""
        packet = bytes([0x3A, 0x00, 0x3A])
        cmd, data = parse_response(packet)

        assert cmd == 0x3A
        assert data == b""

    def test_parse_response_with_data(self):
        """Test parsing response with data."""
        cmd = 0x4B
        payload = bytes([0x01, 0x02, 0x03])
        checksum = (cmd + len(payload) + sum(payload)) & 0xFF
        packet = bytes([cmd, len(payload)]) + payload + bytes([checksum])

        parsed_cmd, parsed_data = parse_response(packet)

        assert parsed_cmd == cmd
        assert parsed_data == payload

    def test_parse_response_invalid(self):
        """Test parsing invalid packet."""
        packet = bytes([0x3A, 0x00, 0x00])  # Bad checksum
        cmd, data = parse_response(packet)

        assert cmd is None
        assert data is None


class TestDecodeErrors:
    """Tests for error code decoding."""

    def test_decode_errors_none(self):
        """Test no errors."""
        errors = decode_errors(0x0000)
        assert errors == []

    def test_decode_errors_single(self):
        """Test single error bit."""
        errors = decode_errors(0x0002)  # Bit 1 = Over Voltage
        assert "Over Voltage" in errors

    def test_decode_errors_multiple(self):
        """Test multiple error bits."""
        # Bit 1 (Over Voltage) + Bit 2 (Low Voltage) + Bit 6 (Controller Over Temp)
        errors = decode_errors(0x0046)
        assert "Over Voltage" in errors
        assert "Low Voltage" in errors
        assert "Controller Over Temp" in errors


class TestCommands:
    """Tests for command constants."""

    def test_monitor_commands(self):
        """Test monitor command values."""
        assert Commands.MONITOR_ONE == 0x3A
        assert Commands.MONITOR_TWO == 0x3B
        assert Commands.MONITOR_THREE == 0x3C

    def test_config_commands(self):
        """Test config command values."""
        assert Commands.READ_CONFIG == 0x4B
        assert Commands.WRITE_CONFIG == 0x4C

    def test_other_commands(self):
        """Test other command values."""
        assert Commands.GET_VERSION == 0x11
        assert Commands.GET_PHASE_I_AD == 0x35


class TestConstants:
    """Tests for protocol constants."""

    def test_baud_rate(self):
        """Test baud rate constant."""
        assert BAUD_RATE == 19200
