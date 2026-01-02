"""
Kelly Motor Controller Packet Parser
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .protocol import CALIBRATION_PARAMS, Commands


@dataclass
class MonitorData:
    """Container for monitor packet data."""

    # Monitor packet 1 (0x3A)
    tps_pedal: int = 0
    brake_pedal: int = 0
    brake_sw1: int = 0
    foot_sw: int = 0
    forward_sw: int = 0
    reverse_sw: int = 0
    hall_a: int = 0
    hall_b: int = 0
    hall_c: int = 0
    battery_voltage: int = 0
    motor_temp: int = 0
    controller_temp: int = 0
    setting_dir: int = 0
    actual_dir: int = 0
    brake_sw2: int = 0
    low_speed: int = 0

    # Monitor packet 2 (0x3B)
    motor_speed: int = 0  # RPM
    phase_current: int = 0

    # Monitor packet 3 (0x3C) - add fields as needed
    error_code: int = 0


class Parser:
    """Parses Kelly controller response packets."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.monitor = MonitorData()
        self._config_data: bytes = b""

    def parse_response(self, cmd: int, data: bytes) -> bool:
        """
        Parse a response packet based on command type.

        Args:
            cmd: Command byte from response
            data: Response data bytes

        Returns:
            True if parsed successfully
        """
        if cmd == Commands.MONITOR_ONE:
            return self._parse_monitor_one(data)
        elif cmd == Commands.MONITOR_TWO:
            return self._parse_monitor_two(data)
        elif cmd == Commands.MONITOR_THREE:
            return self._parse_monitor_three(data)
        elif cmd == Commands.READ_CONFIG:
            return self._parse_config(data)
        elif cmd == Commands.GET_VERSION:
            return self._parse_version(data)
        else:
            if self.debug:
                print(f"[?] Unknown command: 0x{cmd:02X}")
            return False

    def _parse_monitor_one(self, data: bytes) -> bool:
        """Parse monitor packet 1 (0x3A)."""
        if len(data) < 16:
            return False

        self.monitor.tps_pedal = data[0]
        self.monitor.brake_pedal = data[1]
        self.monitor.brake_sw1 = data[2]
        self.monitor.foot_sw = data[3]
        self.monitor.forward_sw = data[4]
        self.monitor.reverse_sw = data[5]
        self.monitor.hall_a = data[6]
        self.monitor.hall_b = data[7]
        self.monitor.hall_c = data[8]
        self.monitor.battery_voltage = data[9]
        self.monitor.motor_temp = data[10]
        self.monitor.controller_temp = data[11]
        self.monitor.setting_dir = data[12]
        self.monitor.actual_dir = data[13]
        self.monitor.brake_sw2 = data[14]
        self.monitor.low_speed = data[15]

        if self.debug:
            print("[+] Parsed monitor packet 1")
        return True

    def _parse_monitor_two(self, data: bytes) -> bool:
        """Parse monitor packet 2 (0x3B)."""
        if len(data) < 6:
            return False

        # Motor speed is 16-bit value at offset 3-4 (big-endian)
        self.monitor.motor_speed = (data[3] << 8) | data[4]
        self.monitor.phase_current = data[5]

        if self.debug:
            print(f"[+] Parsed monitor packet 2: RPM={self.monitor.motor_speed}")
        return True

    def _parse_monitor_three(self, data: bytes) -> bool:
        """Parse monitor packet 3 (0x3C)."""
        if len(data) < 2:
            return False

        # Error code is typically 16-bit
        self.monitor.error_code = (data[0] << 8) | data[1] if len(data) >= 2 else 0

        if self.debug:
            print("[+] Parsed monitor packet 3")
        return True

    def _parse_config(self, data: bytes) -> bool:
        """Parse configuration/calibration data (0x4B)."""
        self._config_data = data
        if self.debug:
            print(f"[+] Received config data: {len(data)} bytes")
        return True

    def _parse_version(self, data: bytes) -> bool:
        """Parse version response (0x11)."""
        if self.debug:
            print(f"[+] Version data: {data.hex()}")
        return True

    def get_config_value(self, param_name: str) -> Optional[Any]:
        """
        Get a configuration parameter value.

        Args:
            param_name: Parameter name from CALIBRATION_PARAMS

        Returns:
            Parameter value or None if not available
        """
        if not self._config_data:
            return None

        if param_name not in CALIBRATION_PARAMS:
            return None

        param = CALIBRATION_PARAMS[param_name]
        offset = param["offset"]
        param_type = param["type"]
        fmt = param["format"]

        if offset >= len(self._config_data):
            return None

        if param_type == 0:  # Bit
            bit = param.get("bit", 0)
            byte_val = self._config_data[offset]
            return (byte_val >> bit) & 1

        elif param_type == 1:  # Single byte
            val = self._config_data[offset]
            if fmt == "so":  # Signed
                return val if val < 128 else val - 256
            return val

        elif param_type == 2:  # Multi-byte
            length = param.get("length", 2)
            if offset + length > len(self._config_data):
                return None

            if fmt == "a":  # ASCII
                return (
                    self._config_data[offset : offset + length]
                    .decode("ascii", errors="ignore")
                    .rstrip("\x00")
                )
            elif fmt == "h":  # Hex
                return self._config_data[offset : offset + length].hex()
            else:  # Unsigned integer (big-endian)
                value = 0
                for i in range(length):
                    value = (value << 8) | self._config_data[offset + i]
                return value

        return None

    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration parameters as dictionary."""
        result = {}
        for name in CALIBRATION_PARAMS:
            value = self.get_config_value(name)
            if value is not None:
                result[name] = value
        return result

    @property
    def config_data(self) -> bytes:
        """Raw configuration data bytes."""
        return self._config_data
