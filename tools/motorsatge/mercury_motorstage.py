#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#
from basil.dut import Dut
import time
import numpy as np
import tables as tb
import csv
import logging
from tables import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
from matplotlib.backends.backend_pdf import PdfPages
from Tkinter import *
Directory = "/home/silab62/HEP/Scripts/Scripts/Calibration_Curves/"

def Restore_intial_positions(Limit=6e6):
    dut = Dut('motorstage_Pyserial.yaml')
    dut.init()
    # Auto-Referencing Option: With standard PI stages
    dut["ms"]._write_command("FE2", address=1)
    dut["ms"]._write_command("FE2", address=2)
    dut["ms"]._write_command("FE2", address=3)
    # Restore intial positions
    # dut["MotorStage"].Read_Write("MR%d" % Limit, address=1)   # y Move to the Border (In-Out)
    # dut["MotorStage"].Read_Write("MR%d" % Limit, address=2)   # z Move to the Border (Up-Down)
    # dut["MotorStage"].Read_Write("MR%d" % -Limit, address=3)   # x Move to the Border (Left-Right)
    # Check Stages
    # dut["MotorStage"].Read_Write("MR 500000", address=1)  # y
    # dut["MotorStage"].Read_Write("MA3000000", address=1)  # x   (Move to the Middle)

def Plan(self, Size_x=50000, Size_y=-50000, Steps=121, Motor_Delay=3, width=1,
         Directory=Directory, Sourcemeter=False, CurrentLimit=1.000000E-06):
    t0 = time.time()
    if Sourcemeter:
        dut = Dut('Scanning_pyserial.yaml')
        dut.init()
        dut['Sourcemeter'].write(":OUTP ON")
        dut['Sourcemeter'].write("*RST")
        dut['Sourcemeter'].write(":SOUR:VOLT:RANG 60")
        dut['Sourcemeter'].write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", dut['Sourcemeter'].ask("SENS:CURR:PROT?")
        dut['Sourcemeter'].write(":SOUR:FUNC VOLT")
        dut['Sourcemeter'].write(':SOUR:VOLT 50')
        val = dut['Sourcemeter'].ask(":MEAS:CURR?")
        current = val[15:-43]
        print "current", float(current)
#         else:
#             dut = Dut('Mercury_MotorStage_Pyserial.yaml')
#             dut.init()
#         Map = np.zeros(shape=(width, Steps), dtype=np.float64)
#
#         def Move(Size_x=Size_x, b=1, Motor_Delay=Motor_Delay):
#             while (b < width):
#                 print "Getting into Loop No. %d with Step Size %d" % (b, Size_x)
#                 dut["MotorStage"].Read_Write("MR%d" % Size_y, address=1)  # x
#                 for a in range(Steps):
#                     dut["MotorStage"].Read_Write("MR%d" % Size_x, address=3)
#                     TD3 = np.float(dut["MotorStage"].Read_Write("TD", address=3)[2:13])
#                     time.sleep(Motor_Delay)
#                     TT3 = np.float(dut["MotorStage"].Read_Write("TT", address=3)[2:13])
#                     # print "Target Pos = %d,Dynamic Pos = %d" % (TT3, TD3)
#                     if Sourcemeter:
#                        # logging.info('###Take readings from sourcemeter####')
#                         val = dut['Sourcemeter'].ask(":MEAS:CURR?")
#                         current = val[15:-43]
#                     else:
#                         current = random.randint(1, 101)
#                     if Size_x >= 0:
#                         print "Step", a
#                         print "current", float(current)
#                         Map[b - 1, a] = float(current)
#                     else:
#                         print "Step", Steps - 1 - a
#                         print "current", float(current)
#                         Map[b - 1, Steps - 1 - a] = float(current)
#                     if ((TT3 == TD3) & (b < width)):  # To check the border Limits
#                         logging.info('###Found TT3 == TD3------------Reversing the Movement ####')
#                         Size_x = Size_x * (-1)
#                         b = b + 1
#                         Move(Size_x=Size_x, b=b)
#                     with tb.open_file(Directory + "Mercury_MotorStage.h5", "w") as out_file_h5:
#                         out_file_h5.create_array(out_file_h5.root, 'Mercury_MotorStage', Map, "Mercury_MotorStage")
#         Move(Size_x=Size_x)
#         t1 = time.time()
#         print "The time Estimated", t1 - t0

def Plan2(self, Size_x=-50000, Size_y=-100000, Steps=121, Motor_Delay=3, width=1,
          Directory=Directory, Sourcemeter=False, CurrentLimit=1.000000E-06):
    t0 = time.time()
    if Sourcemeter:
        dut = Dut('Scanning_pyserial.yaml')
        dut.init()
        dut['Sourcemeter'].write(":OUTP ON")
        dut['Sourcemeter'].write("*RST")
        dut['Sourcemeter'].write(":SOUR:VOLT:RANG 60")
        dut['Sourcemeter'].write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", dut['Sourcemeter'].ask("SENS:CURR:PROT?")
        dut['Sourcemeter'].write(":SOUR:FUNC VOLT")
        dut['Sourcemeter'].write(':SOUR:VOLT 50')
    else:
        dut = Dut('Mercury_MotorStage_Pyserial.yaml')
        dut.init()
    Map = np.zeros(shape=(width, Steps), dtype=np.float64)

    def Move(Size_x=Size_x, b=1, Motor_Delay=Motor_Delay):
        print "Getting into Loop No. %d with Step Size %d" % (b, Size_x)
        num = input('Should I shift:')
        if num == 1:
            dut["MotorStage"].Read_Write("MR%d" % Size_y, address=1)  # x(in-out)
        num2 = input('Should I move:')
        if num2 == 1:
            for a in range(Steps):
                dut["MotorStage"].Read_Write("MR%d" % Size_x, address=2)
                time.sleep(Motor_Delay)
                if Sourcemeter:
                    val = dut['Sourcemeter'].ask(":MEAS:CURR?")
                    current = val[15:-43]
                else:
                    current = random.randint(1, 101)
                if Size_x >= 0:
                    print "Step", a
                    print "current", float(current)
                    Map[b, a] = float(current)
                with tb.open_file(Directory + "Mercury_MotorStage.h5", "w") as out_file_h5:
                    out_file_h5.create_array(out_file_h5.root, 'Mercury_MotorStage', Map, "Mercury_MotorStage")
    for b in range(Steps):
        Move(Size_x=Size_x, b=b)
    t1 = time.time()
    print "The time Estimated", t1 - t0

def GUI_scan():
    dut = Dut('motorstage_Pyserial.yaml')
    dut.init()
    dut["ms"].GUI(root=Tk())  # x(in-out)
'''
Step1: Restore the intial position with Auto-Referencing Option: With standard PI stages
step2: show GUI to control the motor stage 
'''
Restore_intial_positions()
GUI_scan()
#scan.Plan(Size_x=20000, Steps=442, width=20, Sourcemeter=True, Motor_Delay=2)
#scan.Plan2(Size_x=20000, Steps=150, width=50, Sourcemeter=True, Motor_Delay=2)
