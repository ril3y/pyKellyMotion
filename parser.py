from typing import Optional
import math
from enum import Enum
from time import sleep
from typing import List, ByteString

TIRE_SIZE = 12  # in inches


class PacketType(Enum):
    RESPONSE_MONITOR_ONE = 0x3A
    RESPONSE_MONITOR_TWO = 0x3B
    RESPONSE_MONITOR_THREE = 0x3C


class Parser:
    CMD_QUERY_MONITOR_ONE = [0x3A, 0x00, 0x3A]
    CMD_QUERY_MONITOR_TWO = [0x3B, 0x00, 0x3B]
    CMD_QUERY_MONITOR_THREE = [0x3C, 0x00, 0x3C]

    def __init_(self):
        pass

    def parse_packet_monitor_one(self, pkt):
        self.tps_pedal = pkt[2]
        self.brake_pedal = pkt[3]
        self.brake_sw1 = pkt[4]
        self.foot_sw = pkt[5]
        self.forward_sw = pkt[6]
        self.reverse_sw = pkt[7]
        self.hall_a = pkt[8]
        self.hall_b = pkt[9]
        self.hall_c = pkt[10]
        self.battery_voltage = pkt[11]
        self.motor_temp = pkt[12]
        self.controller_temp = pkt[13]
        self.setting_dir = pkt[14]
        self.actual_dir = pkt[15]
        self.brake_sw2 = pkt[16]
        self.low_speed = pkt[17]

    def parse_packet_monitor_two(self, pkt):
        self.motor_speed = pkt[5]  # This is actually motor RPMs
        self.phase_current = pkt[7]

    def __init__(self):
        pass

    def parse_packet_response(self, buff: List[ByteString]):
        header_byte = buff[0]

        match header_byte:
            case PacketType.RESPONSE_MONITOR_ONE.value:
                self.monitor.parse_packet_monitor_one(buff)
                if self.DEBUG:
                    print(f"[+]Got Monitor Packet Response One.  Size:{len(buff)} byte/s ")
            case PacketType.RESPONSE_MONITOR_TWO.value:
                if self.DEBUG:
                    print(f"[+]Got Monitor Packet Response Two.  Size:{len(buff)} byte/s ")
                self.monitor.parse_packet_monitor_two(buff)

            case PacketType.RESPONSE_MONITOR_THREE.value:
                if self.DEBUG:
                    print(f"[+]Got Monitor Packet Response Three.  Size:{len(buff)} byte/s ")
