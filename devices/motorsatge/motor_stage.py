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
from Tkinter import *
import tkMessageBox
from tkFont import Font
class motorstage(HardwareLayer):
    '''Driver for  Sourcemeter 
    '''
    def __init__(self, intf, conf):
        self.debug = 0
        self.lock = threading.Lock()
        super(motorstage, self).__init__(intf, conf)

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
                #print str(msg)
                answer = self._intf.write(str(msg))
                #print answer
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

    def Distance_Calibration(self, LLimit=-3e6, ULimit=3e6):
        plt.plot([LLimit, LLimit + 1e6, LLimit + 2e6, LLimit + 3e6, ULimit], [0, 1.7, 3.4, 5.1, 6.8], 'ro')
        plt.axis([LLimit, ULimit, 0, 11])
        plt.show()
        
        
    def GUI(self,root =False):
        root.title("x-ray motorstage")
        root.geometry("450x230")
        lblInfo = Label(root, padx=8, font=Font(family='times', size=10), text="A", fg="Black")
        y1, y2, y3 = 30, 85, 140
        lblInfo.place(x=10, y=y1)
        e1 = DoubleVar()  # Relative Distance variable
        spinA = Spinbox(root, from_=-1073741824, to=1073741823, increment=1000, format="%0.2f",
                        textvariable=e1, width=10, font=Font(family='times', size=10))
        spinA.place(x=40, y=y1 - 5)
        
        # MR Initiates a move of relative distance of ncounts from the current target position
        Button(root, fg="black", width=11,
               text="Rel. Step >>", font=Font(family='times', size=9),
               command=lambda: self.read_write("MR%d" % e1.get(), address=1)).place(x=40, y=y1 + 20)
        # MA Starts a move to absolute position n.
        value_MA1 = Entry(root, width=11)
        value_MA1.place(x=130, y=y1 - 5)
        Button(root, fg="black", width=9,
               text="Go To >>", font=Font(family='times', size=9),
               command=lambda: self.read_write("MA%d" % int(re.search(r'\d', value_MA1.get()).group()), address=1)).place(x=130, y=y1 + 20)
               
        # AB1 Stops the motor smoothly with programmed deceleration ramp. (Another command (AB) can be used to make a sudden stop for the motor)
        Button(root, fg="black", width=4,
               text="Abort", font=Font(family='times', size=9),
               command=lambda: self._write_command("AB1", address=1)).place(x=330, y=y1 + 20)
        # FE1 &FE0 causes motor to move in a - and + direction until the reference signal changes state.
        Button(root, fg="black", width=3,
               text="-<<", font=Font(family='times', size=9),
               command=lambda: self._write_command("FE0", address=1)).place(x=210, y=y1 + 20)

        Button(root, fg="black", width=3,
               text=">>+", font=Font(family='times', size=9),
               command=lambda: self._write_command("FE1", address=1)).place(x=290, y=y1 + 20)

        # MA0 Moves motor to zero position
        Button(root, padx=4, bd=1, fg="Red", font=Font(family='times', size=9),
               text="Reset", command=lambda: self._write_command("MA0", address=1)).place(x=245, y=y1 + 20)

        lblInfo = Label(root, padx=8, font=Font(family='times', size=10),
                        text="B", fg="Black", anchor='w').place(x=10, y=y2 + 20)

        e2 = DoubleVar()  # Relative Distance variable
        spinB = Spinbox(root, from_=-1073741824, to=1073741823, increment=1000, format="%0.2f",
                        textvariable=e2, width=10, font=Font(family='times', size=10))
        spinB.place(x=40, y=y2)
        MR2 = Button(root, fg="black", width=11,
                     text="Rel. Step >>", font=Font(family='times', size=9),
                     command=lambda: self.read_write("MR%d" % e2.get(), address=2)).place(x=40, y=y2 + 20)
        value_MA2 = Entry(root, width=11)
        value_MA2.place(x=130, y=y2)
        Button(root, fg="black", width=9,
               text="Go To >>", font=Font(family='times', size=11),
               command=lambda: self.read_write("MA%d" % int(re.search(r'\d+', value_MA2.get()).group()), address=2)).place(x=130, y=y2 + 20)

        # AB1 Stops the motor smoothly with programmed deceleration ramp. (Another command (AB) can be used to make a sudden stop for the motor)
        Button(root, fg="black", width=4,
               text="Abort", font=Font(family='times', size=9),
               command=lambda: self._write_command("AB1", address=2)).place(x=330, y=y2 + 20)
        # FE1 &FE0 causes motor to move in a - and + direction until the reference signal changes state.
        Button(root, fg="black", width=3,
               text="-<<", font=Font(family='times', size=9),
               command=lambda: self._write_command("FE0", address=2)).place(x=210, y=y2 + 20)
        Button(root, fg="black", width=3,
               text=">>+", font=Font(family='times', size=9),
               command=lambda: self._write_command("FE1", address=2)).place(x=290, y=y2 + 20)

        Button(root, padx=4, bd=1, fg="Red", font=Font(family='times', size=9),
               text="Reset", command=lambda: self._write_command("MA0", address=2)).place(x=245, y=y2 + 20)

        lblInfo = Label(root, padx=8, font=Font(family='times', size=10),
                        text="C", fg="Black", anchor='w').place(x=10, y=y3)
        e3 = DoubleVar()  # Relative Distance variable
        spinC = Spinbox(root, from_=-1073741824, to=1073741824, increment=1000, format="%0.2f",
                        textvariable=e3, width=10, font=Font(family='times', size=10))
        spinC.place(x=40, y=y3 + 5)
        Button(root, fg="black", width=11,
               text="Rel. Step >>", font=Font(family='times', size=9),
               command=lambda: self.read_write("MR%d" % e3.get(), address=3)).place(x=40, y=y3 + 20)

        value_MA3 = Entry(root, width=11)
        value_MA3.place(x=130, y=y3)
        Button(root, fg="black", width=9,
               text="Go To >>", font=Font(family='times', size=11),
               command=lambda: self.read_write("MA%d" % int(re.search(r'\d+', value_MA3.get()).group()), address=3)).place(x=130, y=y3 + 20)

        # AB1 Stops the motor smoothly with programmed deceleration ramp. (Another command (AB) can be used to make a sudden stop for the motor)
        Button(root, fg="black", width=4,
               text="Abort", font=Font(family='times', size=9),
               command=lambda: self._write_command("AB1", address=3)).place(x=330, y=y3 + 20)
        # FE1 &FE0 causes motor to move in a - and + direction until the reference signal changes state.
        Button(root, fg="black", width=3,
               text="-<<", font=Font(family='times', size=9),
               command=lambda: self._write_command("FE0", address=3)).place(x=210, y=y3 + 20)
        Button(root, fg="black", width=3,
               text=">>+", font=Font(family='times', size=9),
               command=lambda: self._write_command("FE1", address=3)).place(x=290, y=y3 + 20)

        Button(root, padx=4, bd=1, fg="Red", font=Font(family='times', size=9),
               text="Reset", command=lambda: self.read_write("MA0", address=3)).place(x=245, y=y3 + 20)
        Button(root, text="Exit", bg='red', command=sys.exit).place(x=400, y=y3 + 60)
        root.mainloop()
    