# pyKellyMotion

A Python library for interfacing with Kelly motor controllers via serial communication. This project provides comprehensive monitoring and control capabilities for electric motor systems using Kelly Controllers, commonly found in electric vehicles, e-bikes, and other electric motor applications.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Kelly Controller Background](#kelly-controller-background)
- [Installation](#installation)
- [Hardware Requirements](#hardware-requirements)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Communication Protocol](#communication-protocol)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

pyKellyMotion is a Python interface for Kelly motor controllers, enabling real-time monitoring and control of electric motor systems. The library implements the Kelly controller communication protocol, allowing you to read sensor data, monitor motor performance, and control motor operations through a simple Python API.

**Key Capabilities:**
- Real-time motor parameter monitoring
- Battery voltage and temperature sensing
- Motor speed and current monitoring
- Switch and pedal position reading
- Hall sensor status monitoring
- Motor speed to MPH conversion
- Comprehensive error handling and logging

## Features

### Motor Monitoring
- **Speed Monitoring**: Real-time motor RPM with automatic MPH conversion
- **Temperature Monitoring**: Motor and controller temperature readings
- **Current Monitoring**: Phase current measurement
- **Voltage Monitoring**: Battery voltage monitoring with error handling

### Input/Output Monitoring
- **Pedal Inputs**: Throttle position sensor (TPS) and brake pedal monitoring
- **Switch Inputs**: Forward/reverse, brake switches, foot switch, low speed mode
- **Hall Sensors**: Hall effect sensor A, B, and C status monitoring
- **Direction Control**: Setting and actual direction monitoring

### Communication Features
- **Serial Communication**: Robust serial port handling with automatic error recovery
- **Packet-Based Protocol**: Structured communication using three monitor packet types
- **Configurable Timing**: Adjustable packet intervals and sleep times
- **Debug Mode**: Comprehensive logging and debugging capabilities

## Kelly Controller Background

Kelly Controllers are widely used motor controllers in the electric vehicle industry, particularly popular in:
- Electric bicycles and scooters
- Electric motorcycles
- Golf carts and utility vehicles
- Industrial electric motor applications
- DIY electric vehicle conversions

These controllers use a proprietary serial communication protocol operating at 19200 baud, with three distinct monitor packet types for comprehensive system monitoring.

## Installation

### Prerequisites
- Python 3.6 or higher
- Serial port access (USB-to-serial adapter or built-in serial port)
- Kelly motor controller with serial communication capability

### Required Dependencies
```bash
pip install pyserial blessed
```

### Clone the Repository
```bash
git clone https://github.com/ril3y/pyKellyMotion.git
cd pyKellyMotion
```

### Verify Installation
```bash
python3 -c "import serial; print('PySerial installed successfully')"
```

## Hardware Requirements

### Kelly Controller
- Any Kelly motor controller with serial communication support
- Common models: KLS, KSE, KJR series controllers

### Serial Connection
- **USB-to-Serial Adapter**: For computers without built-in serial ports
- **Direct Serial Port**: Built-in serial port on embedded systems
- **Wiring**: Standard 3-wire serial connection (TX, RX, GND)

### Connection Diagram
```
Kelly Controller          Computer/Device
[Serial Port]     <-->    [USB-to-Serial Adapter]
    TX           ------>      RX
    RX           <------      TX
    GND          ------       GND
```

## Quick Start

### Basic Usage
```python
from kelly_controller import KellyController

# Initialize controller with your serial port
controller = KellyController(comport="/dev/ttyUSB0")  # Linux
# controller = KellyController(comport="COM3")        # Windows

# Start monitoring loop
controller.start_monitor_loop()
```

### Simple Data Reading
```python
# Read current motor parameters
print(f"Motor Speed: {controller.motor_speed} RPM")
print(f"Motor Speed: {controller.motor_mph} MPH")
print(f"Battery Voltage: {controller.battery_voltage}V")
print(f"Motor Temperature: {controller.motor_temp}°C")
print(f"Controller Temperature: {controller.controller_temp}°C")
```

## Usage

### Basic Monitoring Example
```python
from kelly_controller import KellyController
from time import sleep

# Initialize controller
controller = KellyController(comport="/dev/ttyUSB0")

# Custom monitoring loop
while True:
    # Read all sensor data
    controller.query_monitor_data()
    
    # Display key parameters
    print(f"Speed: {controller.motor_speed} RPM ({controller.motor_mph} MPH)")
    print(f"Battery: {controller.battery_voltage}V")
    print(f"Current: {controller.phase_current}A")
    print(f"Motor Temp: {controller.motor_temp}°C")
    print(f"Throttle: {controller.tps_pedal}%")
    
    # Check for faults
    if controller.fault:
        print(f"FAULT: {controller.fault}")
    
    sleep(1)  # Update every second
```

### Custom Packet Handling
```python
from communications import Communications
from parser import Parser

# Initialize communication layer
comm = Communications()
parser = Parser()

# Send custom monitor packet
comm.write_bytes(parser.CMD_QUERY_MONITOR_ONE)
response = comm.read_bytes()

# Parse response
if response:
    parser.parse_packet_response(response)
```

### Event-Driven Monitoring
```python
class MotorMonitor:
    def __init__(self, controller):
        self.controller = controller
        self.callbacks = {}
    
    def register_callback(self, parameter, callback):
        self.callbacks[parameter] = callback
    
    def monitor_loop(self):
        while True:
            # Check for parameter changes
            if 'speed' in self.callbacks:
                self.callbacks['speed'](self.controller.motor_speed)
            
            if 'temperature' in self.callbacks:
                self.callbacks['temperature'](self.controller.motor_temp)
            
            sleep(0.1)

# Usage
def speed_changed(speed):
    if speed > 3000:  # RPM limit
        print("WARNING: High motor speed detected!")

monitor = MotorMonitor(controller)
monitor.register_callback('speed', speed_changed)
monitor.monitor_loop()
```

## API Reference

### KellyController Class

#### Constructor
```python
KellyController(comport: str)
```
- `comport`: Serial port identifier (e.g., "/dev/ttyUSB0", "COM3")

#### Properties

##### Motor Parameters
- `motor_speed`: Motor speed in RPM (int)
- `motor_mph`: Motor speed in MPH (float)
- `phase_current`: Phase current in amperes (int)
- `motor_temp`: Motor temperature in Celsius (int)
- `controller_temp`: Controller temperature in Celsius (int)

##### Battery and Power
- `battery_voltage`: Battery voltage in volts (int)
- `fault`: Current fault status (str)

##### Input Controls
- `tps_pedal`: Throttle position sensor percentage (int)
- `brake_pedal`: Brake pedal position (int)
- `brake_sw1`: Brake switch 1 status (bool)
- `brake_sw2`: Brake switch 2 status (bool)
- `foot_sw`: Foot switch status (bool)
- `forward_sw`: Forward switch status (bool)
- `reverse_sw`: Reverse switch status (bool)
- `low_speed`: Low speed mode status (bool)

##### Hall Sensors
- `hall_a`: Hall sensor A status (bool)
- `hall_b`: Hall sensor B status (bool)
- `hall_c`: Hall sensor C status (bool)

##### Direction Control
- `setting_dir`: Set direction (bool)
- `actual_dir`: Actual direction (bool)

#### Methods
```python
print_monitor_settings()  # Print all current values
```

### Communications Class

#### Methods
```python
start_monitor_loop(sleep_time=0.5, packet_interval=0.5)  # Start monitoring
_write_bytes(packet)  # Send packet to controller
_read_bytes()  # Read response from controller
```

### Parser Class

#### Constants
```python
CMD_QUERY_MONITOR_ONE = [0x3A, 0x00, 0x3A]
CMD_QUERY_MONITOR_TWO = [0x3B, 0x00, 0x3B]
CMD_QUERY_MONITOR_THREE = [0x3C, 0x00, 0x3C]
```

#### Methods
```python
parse_packet_monitor_one(pkt)    # Parse monitor packet type 1
parse_packet_monitor_two(pkt)    # Parse monitor packet type 2
parse_packet_response(buff)      # Parse any packet response
```

## Communication Protocol

### Packet Structure
The Kelly controller uses three monitor packet types:

#### Monitor Packet One (0x3A)
- **Purpose**: Primary sensor and control data
- **Data**: TPS pedal, brake pedal, switches, hall sensors, battery voltage, temperatures
- **Length**: 18 bytes
- **Format**: `[0x3A, 0x00, data_bytes..., checksum]`

#### Monitor Packet Two (0x3B)
- **Purpose**: Motor performance data
- **Data**: Motor speed (RPM), phase current
- **Length**: 8 bytes
- **Format**: `[0x3B, 0x00, data_bytes..., checksum]`

#### Monitor Packet Three (0x3C)
- **Purpose**: Additional monitoring data
- **Data**: Extended sensor readings
- **Length**: Variable
- **Format**: `[0x3C, 0x00, data_bytes..., checksum]`

### Serial Configuration
- **Baud Rate**: 19200
- **Data Bits**: 8
- **Stop Bits**: 1
- **Parity**: None
- **Flow Control**: None

### Timing Requirements
- **Packet Interval**: 500ms (configurable)
- **Response Timeout**: 1000ms
- **Sleep Between Packets**: 500ms (configurable)

## Configuration

### Serial Port Configuration
```python
# Linux/Mac
controller = KellyController(comport="/dev/ttyUSB0")
controller = KellyController(comport="/dev/ttyACM0")

# Windows
controller = KellyController(comport="COM3")
controller = KellyController(comport="COM10")
```

### Tire Size Configuration
```python
# Modify tire size for accurate MPH calculation
controller.TIRE_SIZE = 16  # inches (default: 12)
```

### Debug Mode
```python
# Enable debug output
Communications.DEBUG = True
KellyController.DEBUG = True
```

### Custom Timing
```python
# Adjust monitoring intervals
controller.start_monitor_loop(
    sleep_time=0.3,      # Time between packet send and read
    packet_interval=0.8  # Time between complete cycles
)
```

## Troubleshooting

### Common Issues

#### Serial Port Not Found
```
Error: [Errno 2] No such file or directory: '/dev/ttyUSB0'
```
**Solution**: 
- Check if device is connected: `ls /dev/tty*`
- Verify permissions: `sudo chmod 666 /dev/ttyUSB0`
- Install drivers for USB-to-serial adapter

#### Permission Denied
```
Error: [Errno 13] Permission denied: '/dev/ttyUSB0'
```
**Solution**:
- Add user to dialout group: `sudo usermod -a -G dialout $USER`
- Restart session or reboot
- Alternative: Run with sudo (not recommended)

#### No Response from Controller
**Symptoms**: Serial port opens but no data received
**Solutions**:
- Check wiring: TX/RX may be swapped
- Verify baud rate (19200)
- Confirm controller is powered and operational
- Check for correct serial port selection

#### Incomplete or Corrupted Data
**Symptoms**: Partial readings or unexpected values
**Solutions**:
- Increase sleep times between packets
- Check serial cable quality
- Verify controller firmware compatibility
- Enable debug mode for detailed logging

### Debug Mode
```python
# Enable comprehensive debugging
KellyController.DEBUG = True
Communications.DEBUG = True

# This will output:
# - Packet send/receive details
# - Byte-level communication logs
# - Parser state information
# - Error details
```

### Testing Serial Connection
```python
import serial

# Test basic serial connection
try:
    ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=1)
    print(f"Serial port opened: {ser.name}")
    
    # Send test packet
    ser.write(bytes([0x3A, 0x00, 0x3A]))
    
    # Read response
    response = ser.read(100)
    print(f"Response: {response.hex()}")
    
    ser.close()
except Exception as e:
    print(f"Serial test failed: {e}")
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Run tests before submitting changes

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all public methods
- Include unit tests for new features

### Testing
```bash
# Run basic functionality test
python3 main.py

# Test with your controller
python3 -c "
from kelly_controller import KellyController
controller = KellyController('/dev/ttyUSB0')
print('Controller initialized successfully')
"
```

### Submitting Changes
1. Create a feature branch
2. Make your changes
3. Add tests if applicable
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the communication protocol documentation

## Acknowledgments

- Kelly Controller documentation and protocol specifications
- Python serial communication community
- Electric vehicle hobbyist community

## Version History

- **Current**: Development version - Basic monitoring functionality
- **Planned**: v1.0.0 - Full feature implementation with comprehensive testing

---

**Note**: This project is under active development. Some features may be incomplete or subject to change. Always test thoroughly with your specific Kelly controller model before deploying in production environments.