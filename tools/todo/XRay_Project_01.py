#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#
import binascii
import serial
import time
import sys
from Tkinter import *
from tkFont import Font
import tkMessageBox
from basil.HL.RegisterHardwareLayer import HardwareLayer
import threading
import numpy as np
import tables as tb
from scipy.spatial import distance
import random
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from math import exp, expm1
import matplotlib.patches as mpatches


class XRay(HardwareLayer):
    def __init__(self, intf, conf):
        self.debug = 0
        self.lock = threading.Lock()
        super(XRay, self).__init__(intf, conf)

    def init(self):
        self.read_sensirion()  # clear trash
        self.ask(r"7e230200013102010c25010e2601033a7e")  # set readout every second
        self._adresses = []
        for a in range(16):  # Check all possible addresses
            self.write(bytearray.fromhex("01%d" % (a + 30)) + "TB")  # Tell board address
            if self.get_address(a):
                self._adresses.append(a)

    def write(self, value, Source=True):
        with self.lock:
            msg = value + '\r'  # msg has CR at the end

            # print str(msg)
            self._intf.write(str(msg))

    def read(self):
        with self.lock:
            answer = self._intf._readline()  # the read termination string has to be set to \x03
            return answer

    def _write_command(self, command, address=None):
        if address:
            self.write(bytearray.fromhex("01%d" % (address + 30)) + command)
        else:
            for a in self._adresses:
                self.write(bytearray.fromhex("01%d" % (a + 30)) + command)

    def Read_Write(self, command, address=None):
        if address:
            self.write(bytearray.fromhex("01%d" % (address + 30)) + command)
            x = self.read()
        else:
            self.write(command)
            x = self.read()
        return x

    def get_address(self, address):
        self._write_command("TB", address)
        return self.read()

    def set_position(self, value, address=None, ref=None):
        if ref:
            self.set_ref()
            print 'Readjusting coordinates to reference point'

        if address:
            self._write_command("MR%d" % value, address)
        else:
            self._write_command("MR%d" % value)

    def get_position(self, address=None):
        self._write_command("TP", address)
        resp = self.read()
        print resp

    def get_coordinates(self):
        x = float(str(self.Read_Write("TP", address=1))[2:13])
        y = float(str(self.Read_Write("TP", address=2))[2:13])
        z = float(str(self.Read_Write("TP", address=3))[2:13])
        Vector = np.array([x, y, z])
        return Vector

    def get_Distance(self, vector1, vector2, shift=False):
        dist = distance.euclidean(vector1, vector2)
        if shift:
            dist = dist + shift
        return dist

    def Distance_Calibration(self, LLimit=-3e6, ULimit=3e6, Shift=9.847221786166):
        # Controller=[0,1,2,3,4,5,6,7,8,9,10]
        #Length = [0*Shift,1*Shift,2*Shift,3*Shift,4*Shift,5*Shift,6*Shift,7*Shift,8*Shift,9*Shift,10*Shift]
        Controller = [LLimit, LLimit + 1e6, LLimit + 2e6, 0, ULimit - 2e6, ULimit - 1e6, ULimit]
        Length = [Shift, Shift + 1.7, Shift + 3.4, Shift + 5.1, Shift + 6.8, Shift + 8.5, Shift + 10.2]
        # slope=9.847221786166

        plt.plot(Length, Controller, '-o')
        #red_patch = mpatches.Patch(label='Slope='+str(slope))
        # plt.legend(handles=[red_patch])
        plt.axis([LLimit, ULimit, 0, 10 * Shift])
        plt.xlabel('Current ($\mu$A)')
        plt.ylabel('DoseRate (MRad/hr)')
        plt.savefig('/home/silab62/MasterWork/Distance_Calibration.png')
        plt.show()

    def MotorSettings(self, v=True):
        # MF and MN on and off the motor
        self._write_command("MN", address=1)
        self._write_command("MF", address=1)
        self._write_command("SV%d" % v, address=1)  # speed the Motor

        self._write_command("MN", address=2)
        self._write_command("MF", address=2)
        self._write_command("SV%d" % v, address=2)  # speed the Motor

        self._write_command("MN", address=3)
        self._write_command("MF", address=3)
        self._write_command("SV%d" % v, address=3)  # speed the Motor

    def PositionSettings(self, Home=0, Set=0, v=True):
        if Set == 1:
            self._write_command("MA0", address=1)  # Reset A to Zero Position
            self._write_command("MA0", address=2)  # Reset B to Zero Position
            self._write_command("MA0", address=3)  # Reset C to Zero Position
            self._write_command("MA0", address=0)  # Reset All to Zero Position

        if Home == 1:
            self._write_command("DH", address=1)  # Set position to Home
            self._write_command("FE2", address=1)  # Get PI Standards
            self._write_command("DH%d" % v, address=1)  # Define Home with value

            self._write_command("DH", address=2)  # Set position to Home
            self._write_command("FE2", address=2)  # Get PI Standards
            self._write_command("DH%d" % v, address=2)  # Define Home with value

            self._write_command("DH", address=3)  # Set position to Home
            self._write_command("FE2", address=3)  # Get PI Standards
            self._write_command("DH%d" % v, address=3)  # Define Home with value

    def Motor_mode(self):
        print "=====================MotorStage mode inFormation=======================\n"
        self._write_command("TY", address=1)
        print self.read()
        self._write_command("TY", address=2)
        print self.read()
        self._write_command("TY", address=3)
        print self.read()

# Part for Sensirion Thermohygrometer
 


# Part For JulaboFP50_HP chiller
    def Run_mode(self, Switch=2, SetTemp=2):
        # Circulator in Stop/Start condition:
        if Switch == 1:
            self.write("out_mode_05 1")
            self.read()

        if Switch == 0:
            self.write("out_mode_05 0")
            self.read()

        # Selected working temperature:
        if SetTemp == 0:
            tkMessageBox.showwarning("Warning", "Make Sure that the Chiller is OFF")
            self.write("out_mode_01 0")  # Select T1
        if SetTemp == 1:
            self.write("out_mode_01 1")  # Select T2
            tkMessageBox.showwarning("Warning", "Make Sure that the Chiller is OFF")

        self.write("in_mode_05")
        stat = self.read()
        print "The Chiller is on state", stat

    def TempratureSettings(self, v=True, SetT1=False, SetT2=False):
        if SetT1:
            self.Read_Write('out_sp_00 %d' % v)  # Set T1
            print self.Read_Write('in_sp_00')  # Get T1
        if SetT2:
            self.Read_Write('out_sp_01 %d' % v)  # Set T2
            print self.Read_Write('in_sp_01')  # Get T2

    def TempratureLimits(self, v=False, HT=False, LT=False):
        if HT:
            self.write('out_sp_03 %d' % v)
        if LT:
            self.write('out_sp_04 %d' % v)

    def powerLimits(self, v=False, HP=False, LP=False):
        if HP:
            self.write('out_hil_00 %d' % v)
        if LP:
            self.write('out_hil_01 %d' % v)

    def Chiller_mode(self, Power=0, Temp=0):
        print "=====================Chiller mode inFormation=======================\n"
        if Temp == 1:
            Temp = self.Read_Write("in_pv_00")
            Working_Temp = self.Read_Write("in_mode_01")
            print "Actual bath temperature is ", Temp, "Working Temprature is", Working_Temp
            T1 = self.Read_Write("in_sp_00")  # get T1
            T2 = self.Read_Write("in_sp_01")  # get T2

            self.write("in_sp_03")  # High Temperature warning limit
            LimT2 = unicode(self.read(), errors='ignore')
            self.write("in_sp_04")  # Low Temperature warning limit
            LimT1 = unicode(self.read(), errors='ignore')
            print "Settings for Temprature T1 is ", T1, "Settings for Temprature T2", T2, "High Temperature warning limit is ", LimT2, "Low Temperature warning limit is ", LimT1
        if Power == 1:
            Power = self.Read_Write("in_pv_01")
            self.write("in_hil_00")  # High Power warning limit
            Limpow2 = unicode(self.read(), errors='ignore')
            self.write("in_hil_01")  # Low Power warning limit
            Limpow1 = unicode(self.read(), errors='ignore')
            print "Heating power being used is", Power, "Max Cooling Power is  ", Limpow2, "Max Heating Power is is ", Limpow1
