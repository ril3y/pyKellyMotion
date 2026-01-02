"""
pyKellyMotion - Python library for Kelly motor controllers

A library for interfacing with Kelly motor controllers via serial/UART.
Supports real-time monitoring, configuration read/write, and motor identification.

Protocol reverse engineered from Kelly ACAduserEnglish Android app.

Basic Usage:
    from pykellymotion import KellyController

    controller = KellyController("COM3")
    controller.connect()
    controller.read_monitor()
    print(f"RPM: {controller.rpm}")
    controller.disconnect()
"""

__version__ = "0.1.0"
__author__ = "Riley Porter"
__license__ = "MIT"

from .communications import Communications
from .kelly_controller import KellyController
from .parser import MonitorData, Parser
from .protocol import (
    BAUD_RATE,
    CALIBRATION_PARAMS,
    ERROR_CODES,
    Commands,
    build_packet,
    calculate_checksum,
    decode_errors,
    validate_response,
)

__all__ = [
    # Main interface
    "KellyController",
    # Lower-level access
    "Communications",
    "Parser",
    "MonitorData",
    # Protocol utilities
    "Commands",
    "BAUD_RATE",
    "CALIBRATION_PARAMS",
    "ERROR_CODES",
    "build_packet",
    "calculate_checksum",
    "validate_response",
    "decode_errors",
]
