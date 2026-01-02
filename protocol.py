"""
Kelly Motor Controller Protocol Definitions
Reverse engineered from ACAduserEnglish Android app
"""

from enum import IntEnum
from typing import Dict, Any


class Commands(IntEnum):
    """Kelly controller command bytes."""
    # Monitor commands (real-time data)
    MONITOR_ONE = 0x3A
    MONITOR_TWO = 0x3B
    MONITOR_THREE = 0x3C

    # Info commands
    GET_VERSION = 0x11
    GET_PHASE_I_AD = 0x35

    # Configuration commands
    READ_CONFIG = 0x4B      # Read calibration/config data
    WRITE_CONFIG = 0x4C     # Write calibration/config data (13 bytes)

    # Motor identification commands
    ENTRY_IDENTIFY = 0x43
    CHECK_IDENTIFY_STATUS = 0x44
    QUIT_IDENTIFY = 0x42
    GET_RESOLVER_ANGLE = 0x4D
    GET_HALL_SEQUENCE = 0x4E

    # Flash programming commands
    FLASH_READ_START = 0xF1
    FLASH_READ_BLOCK = 0xF2
    FLASH_WRITE_BLOCK = 0xF3
    FLASH_END = 0xF4
    ERASE_FLASH = 0xB1
    BURNT_FLASH = 0xB2
    BURNT_CHECKSUM = 0xB3
    BURNT_RESET = 0xB4
    CODE_END_ADDRESS = 0xB5
    GET_SEED = 0xE1
    VALIDATE_SEED = 0xE2


class IdentifyStatus(IntEnum):
    """Motor identification status values."""
    ACTIVE = 0xAA
    INACTIVE = 0x55


# Communication settings
BAUD_RATE = 19200
DATA_BITS = 8
PARITY = 'N'
STOP_BITS = 1
TIMEOUT_MS = 300


def calculate_checksum(data: bytes) -> int:
    """
    Calculate checksum for Kelly protocol.
    Checksum is sum of all bytes, truncated to 8 bits.
    """
    return sum(data) & 0xFF


def build_packet(cmd: int, data: bytes = b'') -> bytes:
    """
    Build a Kelly protocol packet.

    Format: [CMD][LENGTH][DATA...][CHECKSUM]
    When LENGTH=0, CHECKSUM equals CMD.
    """
    length = len(data)
    packet = bytes([cmd, length]) + data

    if length == 0:
        checksum = cmd
    else:
        checksum = calculate_checksum(packet)

    return packet + bytes([checksum])


def validate_response(packet: bytes, expected_cmd: int = None) -> bool:
    """
    Validate a received packet's checksum and optionally command.

    Returns True if valid, False otherwise.
    """
    if len(packet) < 3:
        return False

    cmd = packet[0]
    length = packet[1]

    # Check packet is complete
    expected_len = length + 3  # cmd + len + data + checksum
    if len(packet) < expected_len:
        return False

    # Validate checksum
    if length == 0:
        expected_checksum = cmd
    else:
        expected_checksum = calculate_checksum(packet[:length + 2])

    actual_checksum = packet[length + 2]

    if actual_checksum != expected_checksum:
        return False

    # Optionally validate command matches
    if expected_cmd is not None and cmd != expected_cmd:
        return False

    return True


def parse_response(packet: bytes) -> tuple:
    """
    Parse a response packet.

    Returns: (cmd, data) tuple, or (None, None) if invalid.
    """
    if not validate_response(packet):
        return None, None

    cmd = packet[0]
    length = packet[1]
    data = packet[2:2 + length] if length > 0 else b''

    return cmd, data


# Calibration parameter definitions
# Format: (offset, data_type, bit_or_length, format, name, min, max, description)
# data_type: 0=bit, 1=byte, 2=multi-byte (big-endian)
# format: 'uo'=unsigned, 'so'=signed, 'h'=hex, 'a'=ascii

CALIBRATION_PARAMS: Dict[str, Dict[str, Any]] = {
    'module_name': {
        'offset': 0x00,
        'type': 2,
        'length': 8,
        'format': 'a',
        'description': 'Module Name (8 chars ASCII)',
        'readonly': True
    },
    'user_name': {
        'offset': 0x08,
        'type': 2,
        'length': 4,
        'format': 'a',
        'description': 'User Name (4 chars ASCII)',
        'readonly': True
    },
    'serial_number': {
        'offset': 0x0C,
        'type': 2,
        'length': 4,
        'format': 'h',
        'description': 'Serial Number',
        'readonly': True
    },
    'software_version': {
        'offset': 0x10,
        'type': 2,
        'length': 4,
        'format': 'h',
        'description': 'Software Version',
        'readonly': True
    },
    'startup_hpedal': {
        'offset': 0x14,
        'type': 0,
        'bit': 0,
        'format': 'uo',
        'description': 'Startup High Pedal Protection',
        'min': 0, 'max': 1
    },
    'brake_hpedal': {
        'offset': 0x14,
        'type': 0,
        'bit': 1,
        'format': 'uo',
        'description': 'Brake High Pedal Protection',
        'min': 0, 'max': 1
    },
    'ntl_hpedal': {
        'offset': 0x14,
        'type': 0,
        'bit': 2,
        'format': 'uo',
        'description': 'Neutral High Pedal Protection',
        'min': 0, 'max': 1
    },
    'foot_switch': {
        'offset': 0x15,
        'type': 0,
        'bit': 0,
        'format': 'uo',
        'description': 'Foot Switch Enable',
        'min': 0, 'max': 1
    },
    'sw_level': {
        'offset': 0x15,
        'type': 0,
        'bit': 1,
        'format': 'uo',
        'description': 'Switch Level (0=Low, 1=High)',
        'min': 0, 'max': 1
    },
    'controller_type': {
        'offset': 0x15,
        'type': 0,
        'bit': 3,
        'format': 'uo',
        'description': 'Controller Type (0=HIM, 1=KIM)',
        'min': 0, 'max': 1
    },
    'change_dir': {
        'offset': 0x15,
        'type': 0,
        'bit': 7,
        'format': 'uo',
        'description': 'Reverse Motor Direction',
        'min': 0, 'max': 1
    },
    'startup_wait_time': {
        'offset': 0x16,
        'type': 1,
        'format': 'uo',
        'description': 'Startup Wait Time (seconds)',
        'min': 0, 'max': 20
    },
    'controller_voltage': {
        'offset': 0x17,
        'type': 2,
        'length': 2,
        'format': 'uo',
        'description': 'Controller Nominal Voltage',
        'min': 0, 'max': 612,
        'readonly': True
    },
    'low_voltage': {
        'offset': 0x19,
        'type': 2,
        'length': 2,
        'format': 'uo',
        'description': 'Low Voltage Cutoff',
        'min': 0, 'max': 1000
    },
    'over_voltage': {
        'offset': 0x1B,
        'type': 2,
        'length': 2,
        'format': 'uo',
        'description': 'Over Voltage Cutoff',
        'min': 0, 'max': 1000
    },
    'current_percent': {
        'offset': 0x25,
        'type': 1,
        'format': 'uo',
        'description': 'Max Current Percent',
        'min': 20, 'max': 100
    },
    'battery_current_limit': {
        'offset': 0x26,
        'type': 1,
        'format': 'uo',
        'description': 'Battery Current Limit %',
        'min': 20, 'max': 100
    },
    'tps_low': {
        'offset': 0x5C,
        'type': 1,
        'format': 'uo',
        'description': 'TPS Low Fault Threshold %',
        'min': 0, 'max': 20
    },
    'tps_high': {
        'offset': 0x5D,
        'type': 1,
        'format': 'uo',
        'description': 'TPS High Fault Threshold %',
        'min': 80, 'max': 100
    },
    'tps_type': {
        'offset': 0x5F,
        'type': 1,
        'format': 'uo',
        'description': 'TPS Type (0=None, 1=0-5V, 2=1-4V, 3=0-5K)',
        'min': 0, 'max': 3
    },
    'tps_dead_low': {
        'offset': 0x60,
        'type': 1,
        'format': 'uo',
        'description': 'TPS Dead Zone Low %',
        'min': 0, 'max': 80
    },
    'tps_dead_high': {
        'offset': 0x61,
        'type': 1,
        'format': 'uo',
        'description': 'TPS Dead Zone High %',
        'min': 120, 'max': 200
    },
    'max_output_freq': {
        'offset': 0x69,
        'type': 2,
        'length': 2,
        'format': 'uo',
        'description': 'Max Output Frequency (Hz)',
        'min': 50, 'max': 1000
    },
    'max_speed': {
        'offset': 0x6B,
        'type': 2,
        'length': 2,
        'format': 'uo',
        'description': 'Max Speed (RPM)',
        'min': 0, 'max': 60000
    },
    'max_forward_speed': {
        'offset': 0x6D,
        'type': 1,
        'format': 'uo',
        'description': 'Max Forward Speed %',
        'min': 30, 'max': 100
    },
    'max_reverse_speed': {
        'offset': 0x6E,
        'type': 1,
        'format': 'uo',
        'description': 'Max Reverse Speed %',
        'min': 20, 'max': 100
    },
    'regen_brake_percent': {
        'offset': 0xE6,
        'type': 1,
        'format': 'uo',
        'description': 'Release TPS Regen Brake %',
        'min': 0, 'max': 50
    },
    'neutral_brake_percent': {
        'offset': 0xE7,
        'type': 1,
        'format': 'uo',
        'description': 'Neutral Regen Brake %',
        'min': 0, 'max': 50
    },
    'accel_time': {
        'offset': 0xEF,
        'type': 1,
        'format': 'uo',
        'description': 'Acceleration Time (x0.1s)',
        'min': 0, 'max': 250
    },
    'accel_release_time': {
        'offset': 0xF0,
        'type': 1,
        'format': 'uo',
        'description': 'Acceleration Release Time (x0.1s)',
        'min': 0, 'max': 250
    },
    'brake_time': {
        'offset': 0xF1,
        'type': 1,
        'format': 'uo',
        'description': 'Brake Ramp Time (x0.1s)',
        'min': 0, 'max': 250
    },
    'brake_release_time': {
        'offset': 0xF2,
        'type': 1,
        'format': 'uo',
        'description': 'Brake Release Time (x0.1s)',
        'min': 0, 'max': 250
    },
    'motor_poles': {
        'offset': 0x10C,
        'type': 1,
        'format': 'uo',
        'description': 'Motor Poles (pole pairs x2)',
        'min': 2, 'max': 32
    },
    'speed_sensor_type': {
        'offset': 0x10D,
        'type': 1,
        'format': 'uo',
        'description': 'Speed Sensor (0=None, 1=Encoder, 2=Hall, 3=Resolver)',
        'min': 0, 'max': 4
    },
    'motor_temp_sensor': {
        'offset': 0x13E,
        'type': 1,
        'format': 'uo',
        'description': 'Motor Temp Sensor (0=None, 1=KTY83)',
        'min': 0, 'max': 1
    },
    'high_temp_cutoff': {
        'offset': 0x13F,
        'type': 1,
        'format': 'uo',
        'description': 'Motor High Temp Cutoff (C)',
        'min': 60, 'max': 170
    },
    'high_temp_resume': {
        'offset': 0x140,
        'type': 1,
        'format': 'uo',
        'description': 'Motor High Temp Resume (C)',
        'min': 60, 'max': 170
    },
}


# Error code bit definitions
ERROR_CODES = {
    0: 'Identification Error',
    1: 'Over Voltage',
    2: 'Low Voltage',
    3: 'Reserved',
    4: 'Stall',
    5: 'Internal Voltage Fault',
    6: 'Controller Over Temp',
    7: 'Throttle Error (Startup)',
    8: 'Reserved',
    9: 'Internal Reset',
    10: 'Hall Sensor Error',
    11: 'Reserved',
    12: 'Reserved',
    13: 'Reserved',
    14: 'Reserved',
    15: 'Motor Over Temp',
}


def decode_errors(error_word: int) -> list:
    """Decode 16-bit error code into list of error strings."""
    errors = []
    for bit, description in ERROR_CODES.items():
        if error_word & (1 << bit):
            errors.append(description)
    return errors
