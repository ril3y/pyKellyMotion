import serial
import os, sys
from enum import Enum

from kelly_controller import KellyController
#from parser import Monitor
from time import sleep
from blessed import terminal



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    controller = KellyController(comport="COM10")
    #controller.start_monitor_loop()
