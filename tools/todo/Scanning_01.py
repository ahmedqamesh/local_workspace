#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# ------------------------------------------------------------
#
import time
import threading
import numpy as np
from basil.HL.RegisterHardwareLayer import HardwareLayer
from numpy import std
import tables as tb
import csv
import logging
from tables import *
import pandas as pd
import matplotlib.pyplot as plt


class Scanning(HardwareLayer):
    '''Driver for  Sourcemeter 
    '''

    def __init__(self, intf, conf):
        self.debug = 0
        self.lock = threading.Lock()
        super(Scanning, self).__init__(intf, conf)

    def init(self):
        self._adresses = []
        for a in range(16):  # Check all possible addresses
            self.write(bytearray.fromhex("01%d" % (a + 30)) + "TB", msg=True)  # Tell board address
            if self.get_address(a):
                self._adresses.append(a)

    def get_address(self, address):
        self._write_command("TB", address)
        return self.read()

    def write(self, value, msg=False):
        if msg:
            with self.lock:
                msg = value + '\r'  # msg has CR at the end
                # print str(msg)
                answer = self._intf.write(str(msg))
                # print answer
        else:
            answer = self._intf.write(str(value))

        return answer

    def read(self):
        answer = self._intf._readline()
        return answer

    def _write_command(self, command, address=None):
        if address:
            self.write(bytearray.fromhex("01%d" % (address + 30)) + command, msg=True)
        else:
            for a in self._adresses:
                self.write(bytearray.fromhex("01%d" % (a + 30)) + command, msg=True)

    def ask(self, value, Source=True):
        if Source:
            self._intf.write(str(value))
            answer = self._intf._readline()
        else:
            self._intf.write(str(value))
            answer = self._intf._readline()
        return answer

    def Read_Write(self, command, address=None):
        if address:
            self.write(bytearray.fromhex("01%d" % (address + 30)) + command, msg=True)
            x = self.read()
        else:
            for a in self._adresses:
                self.write(bytearray.fromhex("01%d" % (a + 30)) + command, msg=True)
                x = self.read()
        return x

    def Distance_Calibration(self, LLimit=-3e6, ULimit=3e6):
        plt.plot([LLimit, LLimit + 1e6, LLimit + 2e6, LLimit + 3e6, ULimit], [0, 1.7, 3.4, 5.1, 6.8], 'ro')
        plt.axis([LLimit, ULimit, 0, 11])
        plt.show()
