"""
Kelly Motor Controller Interface
"""

import math
from time import sleep
from typing import Any, Dict, Optional

from .communications import Communications
from .parser import MonitorData, Parser
from .protocol import CALIBRATION_PARAMS, Commands, decode_errors


class KellyController:
    """
    High-level interface for Kelly motor controllers.

    Supports monitoring, configuration read/write, and motor identification.
    """

    def __init__(self, comport: str, debug: bool = False):
        """
        Initialize controller interface.

        Args:
            comport: Serial port (e.g., 'COM3' or '/dev/ttyUSB0')
            debug: Enable debug output
        """
        self.debug = debug
        self.comm = Communications(comport, debug)
        self.parser = Parser(debug)
        self.tire_diameter = 12  # inches, for MPH calculation

        self._connected = False
        self._version_data: bytes = b""

    # --- Connection Management ---

    def connect(self) -> bool:
        """Open connection to controller."""
        if self.comm.open():
            self._connected = True
            return True
        return False

    def disconnect(self):
        """Close connection to controller."""
        self.comm.close()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected to controller."""
        return self._connected and self.comm.is_open()

    # --- Monitor Data ---

    @property
    def monitor(self) -> MonitorData:
        """Current monitor data."""
        return self.parser.monitor

    def read_monitor(self) -> bool:
        """
        Read all three monitor packets.

        Returns:
            True if all packets read successfully
        """
        success = True

        for monitor_num in [1, 2, 3]:
            ok, data = self.comm.send_monitor_query(monitor_num)
            if ok:
                cmd = Commands.MONITOR_ONE + (monitor_num - 1)
                self.parser.parse_response(cmd, data)
            else:
                success = False

        return success

    def start_monitor_loop(self, callback=None, interval: float = 0.5):
        """
        Continuously read monitor data.

        Args:
            callback: Optional function called after each read cycle
            interval: Time between read cycles (seconds)
        """
        try:
            while True:
                self.read_monitor()
                if callback:
                    callback(self.monitor)
                else:
                    self.print_monitor()
                sleep(interval)
        except KeyboardInterrupt:
            print("\n[+] Monitor loop stopped")

    def print_monitor(self):
        """Print current monitor values."""
        m = self.monitor
        print("\n" + "=" * 50)
        print("KELLY CONTROLLER MONITOR")
        print("=" * 50)
        print(f"  Throttle:      {m.tps_pedal}%")
        print(f"  Brake Pedal:   {m.brake_pedal}")
        print(f"  Motor Speed:   {m.motor_speed} RPM ({self.motor_mph:.1f} MPH)")
        print(f"  Phase Current: {m.phase_current} A")
        print(f"  Battery:       {m.battery_voltage} V")
        print(f"  Motor Temp:    {m.motor_temp} C")
        print(f"  Ctrl Temp:     {m.controller_temp} C")
        print(f"  Direction:     {'FWD' if m.forward_sw else 'REV' if m.reverse_sw else 'N'}")
        print(f"  Hall Sensors:  A={m.hall_a} B={m.hall_b} C={m.hall_c}")
        if m.error_code:
            errors = decode_errors(m.error_code)
            print(f"  ERRORS:        {', '.join(errors)}")
        print("=" * 50)

    @property
    def motor_mph(self) -> float:
        """Calculate vehicle speed in MPH from motor RPM."""
        # Assumes direct drive; adjust for gear ratio if needed
        rpm = self.monitor.motor_speed
        circumference = self.tire_diameter * math.pi  # inches
        inches_per_min = rpm * circumference
        mph = inches_per_min * 60 / 63360  # 63360 inches per mile
        return mph

    # --- Version Info ---

    def get_version(self) -> Optional[str]:
        """
        Get controller firmware version.

        Returns:
            Version string (hex) or None if failed
        """
        success, data = self.comm.get_version()
        if success:
            self._version_data = data
            return data.hex()
        return None

    # --- Configuration ---

    def read_config(self) -> bool:
        """
        Read controller configuration.

        Returns:
            True if successful
        """
        success, data = self.comm.read_config()
        if success:
            self.parser.parse_response(Commands.READ_CONFIG, data)
            return True
        return False

    def get_config(self, param_name: str) -> Optional[Any]:
        """
        Get a configuration parameter value.

        Args:
            param_name: Parameter name (see CALIBRATION_PARAMS)

        Returns:
            Parameter value or None
        """
        return self.parser.get_config_value(param_name)

    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration parameters."""
        return self.parser.get_all_config()

    def print_config(self):
        """Print all configuration parameters."""
        config = self.get_all_config()
        if not config:
            print("[!] No configuration data available. Call read_config() first.")
            return

        print("\n" + "=" * 60)
        print("KELLY CONTROLLER CONFIGURATION")
        print("=" * 60)

        for name, value in config.items():
            param = CALIBRATION_PARAMS.get(name, {})
            desc = param.get("description", name)
            readonly = " (RO)" if param.get("readonly") else ""
            print(f"  {desc}: {value}{readonly}")

        print("=" * 60)

    def write_config(self, data: bytes) -> bool:
        """
        Write raw configuration data to controller.

        Args:
            data: 13 bytes of configuration data

        Returns:
            True if successful

        WARNING: UNTESTED - Writing has not been validated on real hardware!
        This could potentially brick your controller if incorrect data is sent.
        Use at your own risk. Read operations have been tested and work correctly.
        """
        print("[!] WARNING: write_config() is UNTESTED and may damage your controller!")
        return self.comm.write_config(data)

    # --- Phase Current ---

    def get_phase_current_adc(self) -> Optional[tuple]:
        """
        Get raw phase current ADC values.

        Returns:
            Tuple of (phase_a, phase_b, phase_c) ADC values, or None
        """
        success, data = self.comm.get_phase_current_adc()
        if success and len(data) >= 6:
            a = (data[0] << 8) | data[1]
            b = (data[2] << 8) | data[3]
            c = (data[4] << 8) | data[5]
            return (a, b, c)
        return None

    # --- Motor Identification ---

    def enter_identify_mode(self) -> bool:
        """Enter motor identification/tuning mode."""
        return self.comm.enter_identify_mode()

    def exit_identify_mode(self) -> bool:
        """Exit motor identification mode."""
        return self.comm.exit_identify_mode()

    def is_identify_active(self) -> bool:
        """Check if motor identification is active."""
        status = self.comm.check_identify_status()
        return status == 0xAA

    # --- Convenience Properties ---

    @property
    def throttle(self) -> int:
        """Current throttle position (0-100%)."""
        return self.monitor.tps_pedal

    @property
    def rpm(self) -> int:
        """Current motor RPM."""
        return self.monitor.motor_speed

    @property
    def battery_voltage(self) -> int:
        """Current battery voltage."""
        return self.monitor.battery_voltage

    @property
    def motor_temp(self) -> int:
        """Current motor temperature (C)."""
        return self.monitor.motor_temp

    @property
    def controller_temp(self) -> int:
        """Current controller temperature (C)."""
        return self.monitor.controller_temp

    @property
    def phase_current(self) -> int:
        """Current phase current (A)."""
        return self.monitor.phase_current

    @property
    def is_forward(self) -> bool:
        """True if forward direction selected."""
        return bool(self.monitor.forward_sw)

    @property
    def is_reverse(self) -> bool:
        """True if reverse direction selected."""
        return bool(self.monitor.reverse_sw)

    @property
    def errors(self) -> list:
        """List of current error conditions."""
        return decode_errors(self.monitor.error_code)
