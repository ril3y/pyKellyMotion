"""
Kelly Motor Controller Serial Communications
"""

import serial
from serial.serialutil import SerialException
import sys
from time import sleep
from typing import Optional, Tuple

from protocol import (
    Commands, BAUD_RATE, TIMEOUT_MS,
    build_packet, validate_response, parse_response, calculate_checksum
)


class Communications:
    """Handles serial communication with Kelly motor controller."""

    def __init__(self, comport: str, debug: bool = False):
        self.comport = comport
        self.debug = debug
        self.serial: Optional[serial.Serial] = None

    def open(self) -> bool:
        """Open serial connection to controller."""
        self.serial = serial.Serial()
        self.serial.port = self.comport
        self.serial.baudrate = BAUD_RATE
        self.serial.timeout = TIMEOUT_MS / 1000.0

        try:
            self.serial.open()
            if self.debug:
                print(f"[+] Opened serial port {self.comport}")
            return True

        except FileNotFoundError as e:
            print(f"[!] Serial port not found: {e}")
            return False

        except SerialException as e:
            print(f"[!] Error opening serial port: {e}")
            return False

    def close(self):
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            if self.debug:
                print(f"[+] Closed serial port {self.comport}")

    def is_open(self) -> bool:
        """Check if serial port is open."""
        return self.serial is not None and self.serial.is_open

    def _write_bytes(self, data: bytes) -> bool:
        """Write bytes to serial port."""
        if not self.is_open():
            return False

        try:
            self.serial.write(data)
            self.serial.flush()
            if self.debug:
                print(f"[TX] {data.hex()}")
            return True
        except Exception as e:
            print(f"[!] Write error: {e}")
            return False

    def _read_bytes(self, timeout_ms: int = None) -> bytes:
        """
        Read available bytes from serial port.
        Waits for complete packet based on length byte.
        """
        if not self.is_open():
            return b''

        if timeout_ms is not None:
            old_timeout = self.serial.timeout
            self.serial.timeout = timeout_ms / 1000.0

        try:
            # Read header (cmd + length)
            header = self.serial.read(2)
            if len(header) < 2:
                return b''

            length = header[1]
            # Limit length to 16 max (protocol limit)
            length = min(length, 16)

            # Read data + checksum
            remaining = self.serial.read(length + 1)

            packet = header + remaining

            if self.debug:
                print(f"[RX] {packet.hex()}")

            return packet

        except Exception as e:
            print(f"[!] Read error: {e}")
            return b''

        finally:
            if timeout_ms is not None:
                self.serial.timeout = old_timeout

    def send_command(self, cmd: int, data: bytes = b'', retries: int = 2) -> Tuple[bool, bytes]:
        """
        Send command and receive validated response.

        Args:
            cmd: Command byte
            data: Optional data bytes
            retries: Number of retry attempts

        Returns:
            (success, response_data) tuple
        """
        packet = build_packet(cmd, data)

        for attempt in range(retries + 1):
            # Clear input buffer
            if self.serial:
                self.serial.reset_input_buffer()

            # Send packet
            if not self._write_bytes(packet):
                continue

            # Read response
            response = self._read_bytes()
            if not response:
                if self.debug:
                    print(f"[!] No response (attempt {attempt + 1})")
                continue

            # Validate response
            if not validate_response(response, cmd):
                if self.debug:
                    print(f"[!] Invalid response (attempt {attempt + 1})")
                continue

            # Parse and return data
            _, resp_data = parse_response(response)
            return True, resp_data

        return False, b''

    def send_monitor_query(self, monitor_num: int) -> Tuple[bool, bytes]:
        """
        Send monitor query command.

        Args:
            monitor_num: 1, 2, or 3

        Returns:
            (success, response_data) tuple
        """
        if monitor_num == 1:
            cmd = Commands.MONITOR_ONE
        elif monitor_num == 2:
            cmd = Commands.MONITOR_TWO
        elif monitor_num == 3:
            cmd = Commands.MONITOR_THREE
        else:
            return False, b''

        return self.send_command(cmd)

    def get_version(self) -> Tuple[bool, bytes]:
        """Get controller firmware version."""
        return self.send_command(Commands.GET_VERSION)

    def read_config(self) -> Tuple[bool, bytes]:
        """Read controller configuration/calibration data."""
        return self.send_command(Commands.READ_CONFIG)

    def write_config(self, data: bytes) -> bool:
        """
        Write controller configuration data.

        WARNING: UNTESTED - Use at your own risk!

        Args:
            data: 13 bytes of configuration data

        Returns:
            True if successful
        """
        if len(data) != 13:
            print(f"[!] Config data must be 13 bytes, got {len(data)}")
            return False

        success, _ = self.send_command(Commands.WRITE_CONFIG, data)
        return success

    def get_phase_current_adc(self) -> Tuple[bool, bytes]:
        """Get raw phase current ADC values."""
        return self.send_command(Commands.GET_PHASE_I_AD)

    def enter_identify_mode(self) -> bool:
        """Enter motor identification mode."""
        success, _ = self.send_command(Commands.ENTRY_IDENTIFY)
        return success

    def exit_identify_mode(self) -> bool:
        """Exit motor identification mode."""
        success, _ = self.send_command(Commands.QUIT_IDENTIFY)
        return success

    def check_identify_status(self) -> Optional[int]:
        """
        Check motor identification status.

        Returns:
            0xAA if active, 0x55 if inactive, None if error
        """
        success, data = self.send_command(Commands.CHECK_IDENTIFY_STATUS)
        if success and len(data) >= 1:
            return data[0]
        return None
