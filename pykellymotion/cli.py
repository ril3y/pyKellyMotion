#!/usr/bin/env python3
"""
pyKellyMotion CLI - Command line interface for Kelly motor controllers

Usage:
    kelly-motion <port> [command] [options]

Commands:
    monitor     - Real-time monitoring (default)
    version     - Get firmware version
    config      - Read and display configuration
    phase       - Read phase current ADC values
    identify    - Check motor identification status

Examples:
    kelly-motion COM3
    kelly-motion /dev/ttyUSB0 monitor --interval 0.25
    kelly-motion COM3 config
    kelly-motion /dev/ttyUSB0 version
"""

import argparse
import signal
import sys
from typing import Optional

from . import __version__
from .kelly_controller import KellyController


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n[+] Interrupted, exiting...")
    sys.exit(0)


def cmd_monitor(controller: KellyController, args) -> int:
    """Run continuous monitoring."""
    print(f"[+] Starting monitor (interval: {args.interval}s, Ctrl+C to stop)...")

    try:
        controller.start_monitor_loop(interval=args.interval)
    except KeyboardInterrupt:
        pass

    return 0


def cmd_version(controller: KellyController, args) -> int:
    """Get firmware version."""
    print("[+] Reading firmware version...")
    version = controller.get_version()

    if version:
        print(f"[+] Firmware version: {version}")
        return 0
    else:
        print("[!] Failed to read version")
        return 1


def cmd_config(controller: KellyController, args) -> int:
    """Read and display configuration."""
    print("[+] Reading configuration...")

    if controller.read_config():
        if args.raw:
            # Show raw hex dump
            raw = controller.parser.config_data
            print(f"[+] Raw config data ({len(raw)} bytes):")
            print(f"    {raw.hex()}")
        else:
            controller.print_config()
        return 0
    else:
        print("[!] Failed to read configuration")
        return 1


def cmd_phase(controller: KellyController, args) -> int:
    """Read phase current ADC values."""
    print("[+] Reading phase current ADC...")
    adc = controller.get_phase_current_adc()

    if adc:
        print(f"[+] Phase A: {adc[0]}")
        print(f"[+] Phase B: {adc[1]}")
        print(f"[+] Phase C: {adc[2]}")
        return 0
    else:
        print("[!] Failed to read phase currents")
        return 1


def cmd_identify(controller: KellyController, args) -> int:
    """Check motor identification status."""
    print("[+] Checking identification status...")

    if controller.is_identify_active():
        print("[+] Motor identification: ACTIVE")
    else:
        print("[+] Motor identification: INACTIVE")

    return 0


def cmd_single(controller: KellyController, args) -> int:
    """Single monitor read (for scripting)."""
    if not controller.read_monitor():
        print("[!] Failed to read monitor data")
        return 1

    m = controller.monitor

    if args.json:
        import json

        data = {
            "rpm": m.motor_speed,
            "throttle": m.tps_pedal,
            "battery_voltage": m.battery_voltage,
            "motor_temp": m.motor_temp,
            "controller_temp": m.controller_temp,
            "phase_current": m.phase_current,
            "forward": bool(m.forward_sw),
            "reverse": bool(m.reverse_sw),
            "hall_a": m.hall_a,
            "hall_b": m.hall_b,
            "hall_c": m.hall_c,
            "error_code": m.error_code,
        }
        print(json.dumps(data))
    else:
        print(f"RPM: {m.motor_speed}")
        print(f"Throttle: {m.tps_pedal}%")
        print(f"Battery: {m.battery_voltage}V")
        print(f"Motor Temp: {m.motor_temp}C")
        print(f"Controller Temp: {m.controller_temp}C")
        print(f"Phase Current: {m.phase_current}A")
        print(f"Direction: {'FWD' if m.forward_sw else 'REV' if m.reverse_sw else 'N'}")
        if m.error_code:
            print(f"Errors: {controller.errors}")

    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="kelly-motion",
        description="Kelly Motor Controller CLI tool",
        epilog="Protocol reverse engineered from Kelly ACAduserEnglish Android app.",
    )

    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "port",
        help="Serial port (e.g., COM3, /dev/ttyUSB0)",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug output (show TX/RX packets)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Real-time monitoring")
    monitor_parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=0.5,
        help="Update interval in seconds (default: 0.5)",
    )

    # version command
    subparsers.add_parser("version", help="Get firmware version")

    # config command
    config_parser = subparsers.add_parser("config", help="Read configuration")
    config_parser.add_argument(
        "--raw",
        "-r",
        action="store_true",
        help="Show raw hex dump",
    )

    # phase command
    subparsers.add_parser("phase", help="Read phase current ADC")

    # identify command
    subparsers.add_parser("identify", help="Check motor identification status")

    # single command (for scripting)
    single_parser = subparsers.add_parser("single", help="Single monitor read (for scripting)")
    single_parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output as JSON",
    )

    return parser


def main(args: Optional[list] = None) -> int:
    """Main CLI entry point."""
    signal.signal(signal.SIGINT, signal_handler)

    parser = create_parser()
    parsed = parser.parse_args(args)

    # Default command is monitor
    if parsed.command is None:
        parsed.command = "monitor"
        parsed.interval = 0.5

    # Create controller
    controller = KellyController(parsed.port, debug=parsed.debug)

    print(f"[+] Connecting to Kelly controller on {parsed.port}...")
    if not controller.connect():
        print("[!] Failed to connect")
        return 1

    try:
        # Dispatch to command handler
        commands = {
            "monitor": cmd_monitor,
            "version": cmd_version,
            "config": cmd_config,
            "phase": cmd_phase,
            "identify": cmd_identify,
            "single": cmd_single,
        }

        handler = commands.get(parsed.command)
        if handler:
            return handler(controller, parsed)
        else:
            print(f"[!] Unknown command: {parsed.command}")
            return 1

    finally:
        controller.disconnect()
        print("[+] Disconnected")


if __name__ == "__main__":
    sys.exit(main())
