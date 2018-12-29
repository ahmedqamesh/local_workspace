#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#
import binascii
import serial
import time
import logging
import sys
from Tkinter import *
from tkFont import Font
import tkMessageBox
from basil.HL.RegisterHardwareLayer import HardwareLayer
import threading


class XRay(HardwareLayer):

    '''Driver for the XRay Machine.
    A protocoll via RS232 serial port is descriped in XRay_Project.yaml
    '''

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

    def write(self, value):
        with self.lock:
            msg = value + '\r'  # msg has CR at the end
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
        self._write_command("TP", address=1)
        x = str(self.read())[2:13]
        self._write_command("TP", address=2)
        y = str(self.read())[2:13]
        self._write_command("TP", address=3)
        z = str(self.read())[2:13]
        return x, y, z

    def MotorSettings(self):
        childWindow = Toplevel()
        childWindow.wm_title("Motor Settings")
        childWindow.geometry("280x300")
        childWindow.lblInfo = Label(childWindow, text="----------------------Motor A----------------------", font=Font(family='times', size=10)).place(x=5, y=5)
        # MF and MN on and off the motor
        childWindow.MN1 = Button(childWindow, fg="black",
                                 text="Switch ON", font=Font(family='times', size=9), background="green",
                                 command=lambda: self._write_command("MN", address=1)).place(x=5, y=25)
        childWindow.MF1 = Button(childWindow, fg="black",
                                 text="Switch OFF", font=Font(family='times', size=9), background="red",
                                 command=lambda: self._write_command("MF", address=1)).place(x=70, y=25)
        V1 = StringVar()
        childWindow.spinA = Spinbox(childWindow, from_=0, to=60000, increment=1000, format="%0.2f", textvariable=V1, width=11, font=Font(family='times', size=10))
        childWindow.spinA.place(x=145, y=25)
        childWindow.SV1 = Button(childWindow, fg="black", width=10,
                                 text="Speed up", font=Font(family='times', size=9),
                                 command=lambda: self._write_command("SV%d" % int(re.search(r'\d+', V1.get()).group()), address=1)).place(x=145, y=45)

        childWindow.lblInfo = Label(childWindow, text="----------------------Motor B----------------------", font=Font(family='times', size=10)).place(x=5, y=80)
        # MF and MN on and off the motor
        childWindow.MN1 = Button(childWindow, fg="black",
                                 text="Switch ON", font=Font(family='times', size=9), background="green",
                                 command=lambda: self._write_command("MN", address=2)).place(x=5, y=100)
        childWindow.MF1 = Button(childWindow, fg="black",
                                 text="Switch OFF", font=Font(family='times', size=9), background="red",
                                 command=lambda: self._write_command("MF", address=2)).place(x=70, y=100)
        V2 = StringVar()
        childWindow.spinB = Spinbox(childWindow, from_=0, to=60000, increment=1000, format="%0.2f", textvariable=V2, width=11, font=Font(family='times', size=10))
        childWindow.spinB.place(x=145, y=100)
        childWindow.SV2 = Button(childWindow, fg="black", width=10,
                                 text="Speed up", font=Font(family='times', size=9),
                                 command=lambda: self._write_command("SV%d" % int(re.search(r'\d+', V2.get()).group()), address=2)).place(x=145, y=115)

        childWindow.lblInfo = Label(childWindow, text="----------------------Motor C----------------------", font=Font(family='times', size=10)).place(x=5, y=145)
        # MF and MN on and off the motor
        childWindow.MN1 = Button(childWindow, fg="black",
                                 text="Switch ON", font=Font(family='times', size=9), background="green",
                                 command=lambda: self._write_command("MN", address=3)).place(x=5, y=165)
        childWindow.MF1 = Button(childWindow, fg="black",
                                 text="Switch OFF", font=Font(family='times', size=9), background="red",
                                 command=lambda: self._write_command("MF", address=3)).place(x=70, y=165)
        V3 = StringVar()
        childWindow.spinC = Spinbox(childWindow, from_=0, to=60000, increment=1000, format="%0.2f", textvariable=V3, width=11, font=Font(family='times', size=10))
        childWindow.spinC.place(x=145, y=165)
        childWindow.SV3 = Button(childWindow, fg="black", width=10,
                                 text="Speed up", font=Font(family='times', size=9),
                                 command=lambda: self._write_command("SV%d" % int(re.search(r'\d+', V3.get()).group()), address=3)).place(x=145, y=185)


    def PositionSettings(self, Home=0, Set=0):
        if Set == 1:
            childWindow = Toplevel()
            childWindow.wm_title("Position Settings")
            childWindow.lblBotton = Button(childWindow, text=' Reset A to Zero Position ', command=lambda: self._write_command("MA0", address=1)).grid(row=1, column=0, sticky=W, pady=4)
            childWindow.lblBotton = Button(childWindow, text=' Reset B to Zero Position ', command=lambda: self._write_command("MA0", address=2)).grid(row=2, column=0, sticky=W, pady=4)
            childWindow.lblBotton = Button(childWindow, text=' Reset C to Zero Position ', command=lambda: self._write_command("MA0", address=3)).grid(row=3, column=0, sticky=W, pady=4)
            childWindow.lblBotton = Button(childWindow, text='Reset All to Zero Position', command=lambda: self._write_command("MA0", address=0)).grid(row=4, column=0, sticky=W, pady=4)
            childWindow.lblBotton = Button(childWindow, text='       Save and Quit      ', command=lambda: childWindow.destroy()).grid(row=5, column=0, sticky=W, pady=4)
        if Home == 1:
            childWindow = Toplevel()
            childWindow.wm_title("Define Home Settings")
            childWindow.geometry("280x280")
            childWindow.lblInfo = Label(childWindow, text="----------------------Motor A----------------------", font=Font(family='times', size=10)).place(x=5, y=5)
            childWindow.MN1 = Button(childWindow, fg="black",
                                     text="Set pos. to Home", font=Font(family='times', size=9),
                                     command=lambda: self._write_command("DH", address=1)).place(x=5, y=25)
            childWindow.SV1 = Button(childWindow, fg="black",
                                     text="Get PI Standards", font=Font(family='times', size=9), background="green",
                                     command=lambda: self._write_command("FE2", address=1)).place(x=5, y=50)
            V1 = DoubleVar()
            childWindow.spinA = Spinbox(childWindow, from_=-1073741824, to=1073741823, increment=1, format="%0.2f", textvariable=V1, width=11, font=Font(family='times', size=10))
            childWindow.spinA.place(x=100, y=25)
            childWindow.SV1 = Button(childWindow, fg="black",
                                     text="Define with value", font=Font(family='times', size=9),
                                     command=lambda: self._write_command("DH%d" % V1.get(), address=1)).place(x=100, y=50)

            childWindow.lblInfo = Label(childWindow, text="----------------------Motor B----------------------", font=Font(family='times', size=10)).place(x=5, y=80)
            childWindow.MN1 = Button(childWindow, fg="black",
                                     text="Set pos. to Home", font=Font(family='times', size=9),
                                     command=lambda: self._write_command("DH", address=2)).place(x=5, y=100)
            childWindow.SV = Button(childWindow, fg="black",
                                    text="Get PI Standards", font=Font(family='times', size=9), background="green",
                                    command=lambda: self._write_command("FE2", address=2)).place(x=5, y=120)
            V2 = DoubleVar()
            childWindow.spinB = Spinbox(childWindow, from_=-1073741823, to=1073741823, increment=1, format="%0.2f", textvariable=V2, width=11, font=Font(family='times', size=10))
            childWindow.spinB.place(x=100, y=100)
            childWindow.SV = Button(childWindow, fg="black",
                                    text="Define with value", font=Font(family='times', size=9),
                                    command=lambda: self._write_command("DH%d" % V2.get(), address=2)).place(x=100, y=120)

            childWindow.lblInfo = Label(childWindow, text="----------------------Motor C----------------------", font=Font(family='times', size=10)).place(x=5, y=145)
            childWindow.MN1 = Button(childWindow, fg="black",
                                     text="Set pos. to Home", font=Font(family='times', size=9),
                                     command=lambda: self._write_command("DH", address=3)).place(x=5, y=165)
            childWindow.SV = Button(childWindow, fg="black",
                                    text="Get PI Standards", font=Font(family='times', size=9), background="green",
                                    command=lambda: self._write_command("FE2", address=3)).place(x=5, y=190)
            V3 = DoubleVar()
            childWindow.spinB = Spinbox(childWindow, from_=-1073741823, to=1073741823, increment=1, format="%0.2f", textvariable=V3, width=11, font=Font(family='times', size=10))
            childWindow.spinB.place(x=100, y=165)
            childWindow.SV = Button(childWindow, fg="black",
                                    text="Define with value", font=Font(family='times', size=9),
                                    command=lambda: self._write_command("DH%d" % V3.get(), address=3)).place(x=100, y=190)

            childWindow.lblBotton = Button(childWindow, text='       Ok     ', command=lambda: childWindow.destroy()).place(x=50, y=225)

    def Motor_mode(self):
        print "=====================MotorStage mode inFormation=======================\n"
        self._write_command("TY", address=1)
        print self.read()
        self._write_command("TY", address=2)
        print self.read()
        self._write_command("TY", address=3)
        print self.read()

# Part for Sensirion Thermohygrometer
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
        return values

    def get_humidity(self, min_val=0, max_val=100):
        ret = self.ask(r"7e4600b97e")
        values = []
        for j in range(4):
            if ret[2 + 2 * j] == "7f" and ret[2 + 2 * j + 1] == "ff":
                values.append(None)
            else:
                values.append(self.cal_ret(ret[2 + 2 * j] + ret[2 + 2 * j + 1]))
        return values

    def get_dew_point(self, min_val=-40, max_val=100):
        ret = self.ask(r"7e4800b77e")
        values = []
        for j in range(4):
            if ret[2 + 2 * j] == "7f" and ret[2 + 2 * j + 1] == "ff":
                values.append(None)
            else:
                values.append(self.cal_ret(ret[2 + 2 * j] + ret[2 + 2 * j + 1]))
        return values

    def cal_ret(self, value):
        bits = 16
        value = int(value, 16)
        #"""compute the 2's compliment of int value"""
        if (value & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            value = value - (1 << bits)  # compute negative value
        return float(value) / 100.0  # return positive value as is


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

    def Chiller_mode(self, Power=0, Temp=0):
        print "=====================Chiller mode inFormation=======================\n"
        if Temp == 1:
            self.write("in_pv_00")
            Temp = self.read()
            self.write("in_mode_01")
            Working_Temp = self.read()
            print "Actual bath temperature is ", Temp, "Working Temprature is", Working_Temp
            self.write("in_sp_00")  # get T1
            T1 = self.read()  # unicode(self.read(), errors='ignore')
            self.write("in_sp_01")  # get T2
            T2 = self.read()  # unicode(self.read(), errors='ignore')
            self.write("in_sp_03")  # High Temperature warning limit
            LimT2 = unicode(self.read(), errors='ignore')
            self.write("in_sp_04")  # Low Temperature warning limit
            LimT1 = unicode(self.read(), errors='ignore')
            print "Settings for Temprature T1 is ", T1, "Settings for Temprature T2", T2, "High Temperature warning limit is ", LimT2, "Low Temperature warning limit is ", LimT1
        if Power == 1:
            self.write("in_pv_01")
            Power = self.read()
            self.write("in_hil_00")  # High Power warning limit
            Limpow2 = unicode(self.read(), errors='ignore')
            self.write("in_hil_01")  # Low Power warning limit
            Limpow1 = unicode(self.read(), errors='ignore')
            print "Heating power being used is", Power, "Max Cooling Power is  ", Limpow2, "Max Heating Power is is ", Limpow1

    def TempratureSettings(self):
        childWindow = Toplevel()
        childWindow.wm_title("Temprature Settings")
        childWindow.lblInfo = Label(childWindow, text="Working temperature T1").grid(row=0)
        childWindow.lblInfo = Label(childWindow, text="Working temperature T2").grid(row=1)
        e1 = DoubleVar(childWindow)
        Entry(childWindow, textvariable=e1).grid(row=0, column=1)
        e2 = DoubleVar(childWindow)
        Entry(childWindow, textvariable=e2).grid(row=1, column=1)

        childWindow.lblBotton = Button(childWindow, text='Set T1', command=lambda: Set_Settings(Set=1)).grid(row=0, column=2, sticky=W, pady=4)
        childWindow.lblBotton = Button(childWindow, text='Set T2', command=lambda: Set_Settings(Set=0)).grid(row=1, column=2, sticky=W, pady=4)
        childWindow.lblBotton = Button(childWindow, text='Save and Quit', command=lambda: childWindow.destroy()).grid(row=2, column=1, sticky=W, pady=4)

        def Set_Settings(Set=2):
            if Set == 1:
                self.write('out_sp_00 %d' % e1.get())
                self.read()
                self.write('in_sp_00')  # get T1
                T1 = self.read()  # unicode(self.read(), errors='ignore')
                print "Working Temprature T1 is  Now ", T1, "C"
            if Set == 0:
                self.write('out_sp_01 %d' % e2.get())
#                self.read()
                self.write("in_sp_01")  # get T2
                T2 = self.read()  # unicode(self.read(), errors='ignore')
                print "Working Temprature T2 is Now", T2, "C"

    def TempratureLimits(self):
        childWindow = Toplevel()
        childWindow.wm_title("Temprature Limits")
        childWindow.lblInfo = Label(childWindow, text="High Temp. Warning Limits").grid(row=0)
        childWindow.lblInfo = Label(childWindow, text="Low Temp. Warning Limits").grid(row=1)
        HT = DoubleVar(childWindow)
        Entry(childWindow, textvariable=HT).grid(row=0, column=1)
        LT = DoubleVar(childWindow)
        Entry(childWindow, textvariable=LT).grid(row=1, column=1)

        childWindow.lblBotton = Button(childWindow, text='Set Temprature', command=lambda: self.write('out_sp_03 %d' % HT.get())).grid(row=0, column=2, sticky=W, pady=4)
        childWindow.lblBotton = Button(childWindow, text='Set Temprature', command=lambda: self.write('out_sp_04 %d' % LT.get())).grid(row=1, column=2, sticky=W, pady=4)
        childWindow.lblBotton = Button(childWindow, text='Save and Quit', command=lambda: childWindow.destroy()).grid(row=2, column=1, sticky=W, pady=4)

    def powerLimits(self):
        childWindow = Toplevel()
        childWindow.wm_title("Power Limits")
        childWindow.lblInfo = Label(childWindow, text="Maximum Cooling Power").grid(row=0)
        childWindow.lblInfo = Label(childWindow, text="Maximum Heating Power").grid(row=1)
        HP = DoubleVar(childWindow)
        Entry(childWindow, textvariable=HP).grid(row=0, column=1)
        LP = DoubleVar(childWindow)
        Entry(childWindow, textvariable=LP).grid(row=1, column=1)
        childWindow.lblBotton = Button(childWindow, text='Set power', command=lambda: self.write('out_hil_00 %d' % HP.get())).grid(row=0, column=2, sticky=W, pady=4)
        childWindow.lblBotton = Button(childWindow, text='Set Power', command=lambda: self.write('out_hil_00 %d' % LP.get())).grid(row=1, column=2, sticky=W, pady=4)
        childWindow.lblBotton = Button(childWindow, text='Save and Quit', command=lambda: childWindow.destroy()).grid(row=2, column=1, sticky=W, pady=4)

    def StartUp_Message(self):
        tkMessageBox.showinfo("Say Hello", "Hello World")
        print('')
        '''
    showinfo()
    showwarning()
    showerror ()
    askquestion()
    askokcancel()
    askyesno ()
    askretrycancel ()  
    '''

    def rounded_rect(self, canvas, x, y, w, h, c, linewidth=3):
        canvas.create_arc(x, y, x + 2 * c, y + 2 * c, start=90, extent=90, style="arc", width=linewidth)
        canvas.create_arc(x + w - 2 * c, y + h - 2 * c, x + w, y + h, start=270, extent=90, style="arc", width=linewidth)
        canvas.create_arc(x + w - 2 * c, y, x + w, y + 2 * c, start=0, extent=90, style="arc", width=linewidth)
        canvas.create_arc(x, y + h - 2 * c, x + 2 * c, y + h, start=180, extent=90, style="arc", width=linewidth)
        canvas.create_line(x + c, y, x + w - c, y, width=linewidth)
        canvas.create_line(x + c, y + h, x + w - c, y + h, width=linewidth)
        canvas.create_line(x, y + c, x, y + h - c, width=linewidth)
        canvas.create_line(x + w, y + c, x + w, y + h - c, width=linewidth)
