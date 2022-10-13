import serial
from serial.serialutil import SerialException, SerialTimeoutException
import sys
from time import sleep


class Communications:

    def _write_bytes(self, packet):
        if self.serial.is_open:
            self.serial.write(packet)

    def _read_bytes(self):
        if self.serial.in_waiting > 0:
            bytes_read = self.serial.read(self.serial.in_waiting)
            if self.DEBUG:
                print(f'Read read {len(bytes_read)}')
            return bytes_read

    def start_monitor_loop(self, sleep_time=.5, packet_interval=.5):
        while 1:
            self._write_bytes(bytes(self.MONITOR_PACKET_ONE))
            sleep(sleep_time)
            self.parse_packet_response()

            self._write_bytes(bytes(self.MONITOR_PACKET_TWO))
            sleep(sleep_time)
            self.parse_packet_response()

            self._write_bytes(bytes(self.MONITOR_PACKET_THREE))
            sleep(sleep_time)
            self.parse_packet_response()
            self.monitor.print_monitor_settings()
            sleep(packet_interval)

    def _open_serial_port(self, comport):
        self.serial = serial.Serial()
        self.serial.setPort(comport)
        self.serial.baudrate = 19200
        try:
            self.serial.open()

        except FileNotFoundError as e:
            print(f"[!] Error Opening Serial Port: {e}")

        except SerialException as e:
            print(f"[!] Error Opening Serial Port: {e}")
            sys.exit()

        if not self.serial.is_open:
            print(f"Error opening serial {self.serial.port}.  Exiting....")
        sys.exit()

    def query_motion_controller_monitor(self):
        return [self.CMD_QUERY_MONITOR_ONE, self.CMD_QUERY_MONITOR_TWO, self.CMD_QUERY_MONITOR_THREE]

    @staticmethod
    def get_controller_serial_number(self):
        pass
