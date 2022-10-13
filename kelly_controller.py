from communications import Communications
import serial, sys
from serial.serialutil import SerialException
from time import sleep
import math


class KellyController:
    DEBUG = False

    def __init__(self, comport: str):
        # self._open_serial_port(str)
        # self._tps_pedal: int = None
        # self._brake_pedal: bool = None
        # self._brake_sw1: bool = None
        # self._foot_sw: bool = None
        # self._reverse_sw: bool = None
        # self._hall_a: bool = None
        # self._hall_b: bool = None
        # self._hall_c: bool = None
        # self._battery_voltage: int = None
        # self._motor_temp: int = None
        # self._controller_temp: int = None
        # self._setting_dir: bool = None
        # self._actual_dir: bool = None
        # self._brake_sw2: bool = None
        # self._low_speed: bool = None
        # self._fault: str = None
        # self._motor_speed: int = None
        # self._phase_current: int = None
        # self._forward_sw: bool = None
        # self._motor_mph: float = None
        self.TIRE_SIZE = 12

    @property
    def motor_mph(self):
        return self._motor_mph

    @motor_mph.setter
    def motor_mph(self, mph):
        # Vehicle speed = Wheels RPM × Tire diameter × π × 60 / 63360
        mph = self._moto_speed
        self._motor_mph = mph * (self.TIRE_SIZE / 2) * math.pi * 60 / 63360
        self._motor_mph = "%.2f" % self._motor_mph

    @property
    def motor_speed(self):
        return self._motor_speed

    @motor_speed.setter
    def motor_speed(self, motor_speed):
        if motor_speed >= 0 and motor_speed is not None:
            self._motor_speed = motor_speed
        else:
            raise ValueError(f"Error setting motor speed {motor_speed}.")

    @property
    def brake_sw2(self):
        return self._brake_sw2

    @brake_sw2.setter
    def brake_sw2(self, brake_sw2):
        self._brake_sw2 = brake_sw2

    @property
    def actual_dir(self):
        return self._actual_dir

    @actual_dir.setter
    def actual_dir(self, actual_dir):
        self._actual_dir = actual_dir

    @property
    def setting_dir(self):
        return self._setting_dir

    @setting_dir.setter
    def setting_dir(self, setting_dir):
        self._setting_dir = setting_dir

    @property
    def motor_temp(self):
        return self._motor_speed

    @motor_temp.setter
    def motor_temp(self, motor_temp):
        self._motor_temp = motor_temp

    @property
    def low_speed(self):
        return self._low_speed

    @low_speed.setter
    def low_speed(self, low_speed):
        self._low_speed = low_speed

    @property
    def phase_current(self):
        return self._phase_current

    @phase_current.setter
    def phase_current(self, phase_current):
        self._phase_current = phase_current

    @property
    def hall_a(self):
        return self._hall_a

    @hall_a.setter
    def hall_a(self, hall_a):
        self._hall_a = hall_a

    @property
    def hall_b(self):
        return self._hall_b

    @hall_b.setter
    def hall_b(self, hall_b):
        self._hall_b = hall_b

    @property
    def hall_c(self):
        return self._hall_c

    @hall_c.setter
    def hall_c(self, hall_c):
        self._hall_c = hall_c

    @property
    def foot_sw(self):
        return self._foot_sw

    @foot_sw.setter
    def foot_sw(self, foot_sw):
        self._foot_sw = foot_sw

    @property
    def reverse_sw(self):
        return self._reverse_sw

    @reverse_sw.setter
    def reverse_sw(self, reverse):
        self._reverse_sw = reverse

    @property
    def forward_sw(self):
        return self._forward_sw

    @forward_sw.setter
    def forward_sw(self, forward):
        self._forward_sw = forward

    @property
    def tps_pedal(self):
        return self._tps_pedal

    @tps_pedal.setter
    def tps_pedal(self, tps_pedal):
        self._tps_pedal = tps_pedal

    @property
    def brake_pedal(self):
        return self._brake_pedal

    @brake_pedal.setter
    def brake_pedal(self, brake_pedal):
        self._brake_pedal = brake_pedal

    @property
    def brake_sw1(self):
        return self._brake_sw1

    @brake_sw1.setter
    def brake_sw1(self, brake_sw1: bool):
        self._brake_sw1 = brake_sw1

    @property
    def controller_temp(self):
        return self._controller_temp

    @controller_temp.setter
    def controller_temp(self, temp):
        self._controller_temp = temp

    @property
    def battery_voltage(self):
        return self._battery_voltage

    @battery_voltage.setter
    def battery_voltage(self, voltage):
        try:
            if voltage > 0:
                self._battery_voltage = voltage
            else:
                raise ValueError("Voltage cannot be a negative value.")
        except ValueError as e:
            print(e)

        except TypeError as e:
            print(e)

    def print_monitor_settings(self):
        # The following values are from the 1st monitor packet (0x3A header)
        print(f"[+]Monitor Packet:")
        print(f"\t[*]TPS Pedal: {self.tps_pedal}")
        print(f"\t[*]Brake Pedal: {self.brake_pedal}")
        print(f"\t[*]Brake SW1: {self.brake_sw1}")

        print(f"\t[*]Forward SW1: {self.forward_sw}")
        print(f"\t[*]Reverse SW1: {self.reverse_sw}")
        print(f"\t[*]Hall A: {self.hall_a}")
        print(f"\t[*]Hall B: {self.hall_b}")
        print(f"\t[*]Hall C: {self.hall_c}")

        print(f"\t[*]Battery Voltage: {self.battery_voltage}")
        print(f"\t[*]Motor Temp: {self.motor_temp}")
        print(f"\t[*]Controller Temp: {self.controller_temp}")
        print(f"\t[*]Setting Direction: {self.setting_dir}")
        print(f"\t[*]Actual Dir: {self.actual_dir}")
        print(f"\t[*]Brake SW2: {self.brake_sw2}")
        print(f"\t[*]Low Speed: {self.low_speed}")

        # The following values are from the 1st monitor packet (0x3A header)
        print(f"\t[*]Motor Speed: {self.motor_speed}")
        print(f"\t[*]Phase Current: {self.phase_current}")
        print(f"\t[*]Miles Per Hour (MPH): {self.motor_mph}")  # This is not part of the packet
