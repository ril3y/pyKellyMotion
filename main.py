#!/usr/bin/env python3
"""
Kelly Motor Controller Example Usage
"""

import sys
from kelly_controller import KellyController


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <COM_PORT> [command]")
        print("")
        print("Commands:")
        print("  monitor   - Start real-time monitoring (default)")
        print("  version   - Get firmware version")
        print("  config    - Read and display configuration")
        print("  phase     - Read phase current ADC values")
        print("")
        print("Examples:")
        print("  python main.py COM3")
        print("  python main.py /dev/ttyUSB0 config")
        return

    port = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "monitor"

    # Create controller instance
    controller = KellyController(port, debug=False)

    print(f"[+] Connecting to Kelly controller on {port}...")
    if not controller.connect():
        print("[!] Failed to connect")
        return

    try:
        if command == "version":
            print("[+] Reading firmware version...")
            version = controller.get_version()
            if version:
                print(f"[+] Firmware version: {version}")
            else:
                print("[!] Failed to read version")

        elif command == "config":
            print("[+] Reading configuration...")
            if controller.read_config():
                controller.print_config()
            else:
                print("[!] Failed to read configuration")

        elif command == "phase":
            print("[+] Reading phase current ADC...")
            adc = controller.get_phase_current_adc()
            if adc:
                print(f"[+] Phase A: {adc[0]}")
                print(f"[+] Phase B: {adc[1]}")
                print(f"[+] Phase C: {adc[2]}")
            else:
                print("[!] Failed to read phase currents")

        elif command == "monitor":
            print("[+] Starting monitor loop (Ctrl+C to stop)...")
            controller.start_monitor_loop(interval=0.5)

        else:
            print(f"[!] Unknown command: {command}")

    finally:
        controller.disconnect()
        print("[+] Disconnected")


if __name__ == "__main__":
    main()
