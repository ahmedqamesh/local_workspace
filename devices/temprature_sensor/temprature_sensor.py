#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# ------------------------------------------------------------
#
import binascii
import serial
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
from Tkinter import *
import tkMessageBox
from tkFont import Font
class temprature_sensor(HardwareLayer):
    '''Driver for  Sourcemeter 
    '''
    def __init__(self, intf, conf):
        self.debug = 0
        self.lock = threading.Lock()
        super(temprature_sensor, self).__init__(intf, conf)

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
                
    def ask(self, value):
        self._intf.write(str(value))
        answer = self._intf._readline()
        return answer
    
    def read_write(self, command, address=None):
        if address:
            self.write(bytearray.fromhex("01%d" % (address + 30)) + command, msg=True)
            x = self.read()
        else:
            for a in self._adresses:
                self.write(bytearray.fromhex("01%d" % (a + 30)) + command, msg=True)
                x = self.read()
        return x

    def write_sensirion(self, command):
        self._intf.write(binascii.a2b_hex(command))

    def ask(self, command):
        '''Read response to command and convert it to 16-bit integer.
        Returns : list of values
        '''
        self.write_sensirion(command)
        time.sleep(0.1)
        return self.read_sensirion()

    def read_sensirion(self):
        Result = []
        flg = 0
        for i in range(1024):  # data assumed to be less than 1024 words
            a = self._intf.read(size=1).encode('hex_codec')
            if self.debug == 1:
                print a,
            if a == '':
                if self.debug == 1:
                    print "sensirionEKH4.read() timeout"
                break
            elif flg == 0 and a == '7e':
                flg = 1
            elif flg == 1 and a == '7e':
                break
            elif flg == 1:
                Result.append(a)
        if self.debug == 1:
            print "----", Result
        return Result

    def get_temperature(self, min_val=-40, max_val=200):
        ret = self.ask(r"7e4700b87e")
        values = []
        for j in range(4):
            if ret[2 + 2 * j] == "7f" and ret[2 + 2 * j + 1] == "ff":
                values.append(None)
            else:
                values.append(self.cal_ret(ret[2 + 2 * j] + ret[2 + 2 * j + 1]))
        return values[0]

    def get_humidity(self, min_val=0, max_val=100):
        ret = self.ask(r"7e4600b97e")
        values = []
        for j in range(4):
            if ret[2 + 2 * j] == "7f" and ret[2 + 2 * j + 1] == "ff":
                values.append(None)
            else:
                values.append(self.cal_ret(ret[2 + 2 * j] + ret[2 + 2 * j + 1]))
        return values[0]

    def get_dew_point(self, min_val=-40, max_val=100):
        ret = self.ask(r"7e4800b77e")
        values = []
        for j in range(4):
            if ret[2 + 2 * j] == "7f" and ret[2 + 2 * j + 1] == "ff":
                values.append(None)
            else:
                values.append(self.cal_ret(ret[2 + 2 * j] + ret[2 + 2 * j + 1]))
        return values[0]

    def cal_ret(self, value):
        bits = 16
        value = int(value, 16)
        #"""compute the 2's compliment of int value"""
        if (value & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            value = value - (1 << bits)  # compute negative value
        return float(value) / 100.0  # return positive value as is