# pyKellyMotion

A Python library for interfacing with Kelly motor controllers via serial/UART communication. Provides comprehensive monitoring, configuration read/write, and control capabilities for electric motor systems.

**Protocol reverse engineered from Kelly ACAduserEnglish Android app.**

## Features

- **Real-time Monitoring** - Motor speed, temperature, current, voltage, switch states
- **Configuration Read/Write** - Read and modify controller parameters over serial
- **Firmware Version Query** - Get controller firmware information
- **Motor Identification** - Enter/exit motor auto-tuning mode
- **Checksum Validation** - All packets validated for data integrity
- **Clean Pythonic API** - Simple interface with type hints and dataclasses

## Installation

### Prerequisites
- Python 3.7+
- Serial port access (USB-to-serial adapter or built-in UART)

### Install Dependencies
```bash
pip install pyserial
```

### Clone Repository
```bash
git clone https://github.com/ril3y/pyKellyMotion.git
cd pyKellyMotion
```

## Quick Start

### Command Line
```bash
# Real-time monitoring
python main.py COM3

# Get firmware version
python main.py /dev/ttyUSB0 version

# Read controller configuration
python main.py COM3 config

# Read phase current ADC
python main.py /dev/ttyUSB0 phase
```

### Python API
```python
from kelly_controller import KellyController

# Connect
controller = KellyController("COM3", debug=False)
controller.connect()

# Monitor
controller.read_monitor()
print(f"RPM: {controller.rpm}")
print(f"Throttle: {controller.throttle}%")
print(f"Battery: {controller.battery_voltage}V")
print(f"Errors: {controller.errors}")

# Read configuration
controller.read_config()
controller.print_config()
max_current = controller.get_config('current_percent')

# Cleanup
controller.disconnect()
```

## Hardware Setup

### Wiring
```
Kelly Controller          Computer
   TX  ────────────────>  RX
   RX  <────────────────  TX
   GND ─────────────────  GND
```

### Supported Controllers
- **KBLS** - Kelly BLDC Sensorless/Sensored
- **KACI** - Kelly AC Induction
- Other Kelly controllers with serial interface

## API Reference

### KellyController

#### Connection
```python
controller = KellyController(comport: str, debug: bool = False)
controller.connect() -> bool
controller.disconnect()
controller.is_connected -> bool
```

#### Monitoring
```python
controller.read_monitor() -> bool                              # Read all monitor packets
controller.start_monitor_loop(callback=None, interval=0.5)     # Continuous monitoring
controller.print_monitor()                                     # Print formatted data
```

#### Monitor Properties
| Property | Type | Description |
|----------|------|-------------|
| `rpm` | int | Motor speed in RPM |
| `motor_mph` | float | Speed in MPH (uses tire_diameter) |
| `throttle` | int | Throttle position 0-100% |
| `phase_current` | int | Phase current in amps |
| `battery_voltage` | int | Battery voltage |
| `motor_temp` | int | Motor temperature (C) |
| `controller_temp` | int | Controller temperature (C) |
| `is_forward` | bool | Forward direction selected |
| `is_reverse` | bool | Reverse direction selected |
| `errors` | list | Current error strings |

#### Configuration
```python
controller.read_config() -> bool                    # Read config from controller
controller.get_config(param_name: str) -> Any       # Get specific parameter
controller.get_all_config() -> dict                 # Get all parameters
controller.print_config()                           # Print formatted config
controller.write_config(data: bytes) -> bool        # Write raw config (13 bytes) - UNTESTED!
```

> **WARNING:** `write_config()` has NOT been tested on real hardware. Read operations work correctly, but writing could potentially damage your controller. Use at your own risk!

#### Other Commands
```python
controller.get_version() -> str                     # Firmware version (hex)
controller.get_phase_current_adc() -> tuple         # Raw ADC (a, b, c)
controller.enter_identify_mode() -> bool            # Enter motor auto-tune
controller.exit_identify_mode() -> bool             # Exit motor auto-tune
controller.is_identify_active() -> bool             # Check if tuning active
```

### Configuration Parameters

| Parameter | Description | Range |
|-----------|-------------|-------|
| `module_name` | Module identifier | 8 chars ASCII |
| `serial_number` | Serial number | Hex |
| `software_version` | Firmware version | Hex |
| `current_percent` | Max current limit | 20-100% |
| `battery_current_limit` | Battery current limit | 20-100% |
| `low_voltage` | Undervoltage cutoff | 0-1000V |
| `over_voltage` | Overvoltage cutoff | 0-1000V |
| `max_speed` | Maximum RPM | 0-60000 |
| `max_forward_speed` | Forward speed limit | 30-100% |
| `max_reverse_speed` | Reverse speed limit | 20-100% |
| `tps_type` | Throttle type | 0=None, 1=0-5V, 2=1-4V, 3=0-5K |
| `tps_dead_low` | Throttle dead zone low | 0-80% |
| `tps_dead_high` | Throttle dead zone high | 120-200% |
| `accel_time` | Acceleration ramp (x0.1s) | 0-250 |
| `brake_time` | Brake ramp (x0.1s) | 0-250 |
| `regen_brake_percent` | Regen on throttle release | 0-50% |
| `motor_poles` | Motor pole pairs x2 | 2-32 |
| `speed_sensor_type` | 0=None, 1=Encoder, 2=Hall, 3=Resolver | 0-4 |
| `high_temp_cutoff` | Motor overtemp cutoff | 60-170C |

## Communication Protocol

### Serial Settings
| Parameter | Value |
|-----------|-------|
| Baud Rate | 19200 |
| Data Bits | 8 |
| Parity | None |
| Stop Bits | 1 |

### Packet Structure
```
[CMD] [LENGTH] [DATA...] [CHECKSUM]
```

| Field | Size | Description |
|-------|------|-------------|
| CMD | 1 byte | Command ID |
| LENGTH | 1 byte | Data byte count (0-16) |
| DATA | 0-16 bytes | Command-specific data |
| CHECKSUM | 1 byte | `sum(preceding_bytes) & 0xFF` |

**Special case:** When LENGTH = 0, CHECKSUM equals CMD.

### Commands

| Command | Hex | Description |
|---------|-----|-------------|
| MONITOR_ONE | 0x3A | Real-time data page 1 (throttle, switches, temps) |
| MONITOR_TWO | 0x3B | Real-time data page 2 (RPM, current) |
| MONITOR_THREE | 0x3C | Real-time data page 3 (errors) |
| GET_VERSION | 0x11 | Firmware version |
| READ_CONFIG | 0x4B | Read configuration/calibration |
| WRITE_CONFIG | 0x4C | Write configuration (13 bytes) |
| GET_PHASE_I_AD | 0x35 | Phase current ADC values |
| ENTRY_IDENTIFY | 0x43 | Enter motor identification mode |
| QUIT_IDENTIFY | 0x42 | Exit motor identification mode |
| CHECK_IDENTIFY_STATUS | 0x44 | Check identification status |

### Protocol Examples

**Read Monitor Data:**
```
TX: 3A 00 3A
RX: 3A 10 [16 bytes data] [checksum]
```

**Read Configuration:**
```
TX: 4B 00 4B
RX: 4B [len] [config data] [checksum]
```

**Get Version:**
```
TX: 11 00 11
RX: 11 [len] [version data] [checksum]
```

## Project Structure

```
pyKellyMotion/
├── protocol.py          # Protocol constants, commands, checksum
├── communications.py    # Serial communication layer
├── parser.py            # Packet parsing and data extraction
├── kelly_controller.py  # High-level controller interface
└── main.py              # CLI entry point
```

## Advanced Usage

### Custom Monitor Callback
```python
def my_callback(monitor_data):
    print(f"Speed: {monitor_data.motor_speed} RPM")
    if monitor_data.motor_temp > 80:
        print("WARNING: Motor hot!")

controller.start_monitor_loop(callback=my_callback, interval=0.25)
```

### Direct Command Access
```python
from communications import Communications
from protocol import Commands

comm = Communications("COM3", debug=True)
comm.open()

success, data = comm.send_command(Commands.GET_VERSION)
print(f"Version: {data.hex()}")

comm.close()
```

### Debug Mode
```python
controller = KellyController("COM3", debug=True)
# Shows TX/RX packets in hex
```

## Error Codes

16-bit bitmask decoded by `controller.errors`:

| Bit | Error |
|-----|-------|
| 0 | Identification Error |
| 1 | Over Voltage |
| 2 | Low Voltage |
| 4 | Stall |
| 5 | Internal Voltage Fault |
| 6 | Controller Over Temp |
| 7 | Throttle Error (Startup) |
| 9 | Internal Reset |
| 10 | Hall Sensor Error |
| 15 | Motor Over Temp |

## Troubleshooting

### No Response
- Check TX/RX wiring (may need swap)
- Verify 19200 baud
- Ensure controller powered
- Enable `debug=True`

### Permission Denied (Linux)
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Checksum Errors
- Check cable quality
- Ensure clean ground connection

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- Protocol reverse engineered from Kelly ACAduserEnglish Android app
- Kelly Controller motor controller products
- Electric vehicle hobbyist community
