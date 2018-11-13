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
from basil.dut import Dut
from Tkinter import *
import tkMessageBox
from tkFont import Font

class Class():
    Directory = "/home/silab62/HEP/Scripts/Scripts/Calibration_Curves/"

    def Restore_intial_positions(self, Limit=6e6):
        dut = Dut('Mercury_MotorStage_Pyserial.yaml')
        dut.init()
        for a in range(70):
            dut["MotorStage"].Read_Write("MR -50000", address=1)  # x
            time.sleep(3)
            print a

#         # Auto-Referencing Option: With standard PI stages
#         dut["MotorStage"]._write_command("FE2", address=1)
#         dut["MotorStage"]._write_command("FE2", address=2)
#         dut["MotorStage"]._write_command("FE2", address=3)
        # Restore intial positions
        # dut["MotorStage"].Read_Write("MR%d" % Limit, address=1)   # y Move to the Border (In-Out)
        # dut["MotorStage"].Read_Write("MR%d" % Limit, address=2)   # z Move to the Border (Up-Down)
        # dut["MotorStage"].Read_Write("MR%d" % -Limit, address=3)   # x Move to the Border (Left-Right)
        # Check Stages
        # dut["MotorStage"].Read_Write("MR 500000", address=1)  # y
        # dut["MotorStage"].Read_Write("MA3000000", address=1)  # x   (Move to the Middle)

    def Calibration(self):
        dut = Dut('Mercury_MotorStage_Pyserial.yaml')
        dut.init()
        root = Tk()
        root.title("X-Ray Calibration")
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
               command=lambda: dut["MotorStage"].Read_Write("MR%d" % e1.get(), address=1)).place(x=40, y=y1 + 20)
        # MA Starts a move to absolute position n.
        value_MA1 = Entry(root, width=11)
        value_MA1.place(x=130, y=y1 - 5)
        Button(root, fg="black", width=9,
               text="Go To >>", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"].Read_Write("MA%d" % int(re.search(r'\d', value_MA1.get()).group()), address=1)).place(x=130, y=y1 + 20)

        # AB1 Stops the motor smoothly with programmed deceleration ramp. (Another command (AB) can be used to make a sudden stop for the motor)
        Button(root, fg="black", width=4,
               text="Abort", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("AB1", address=1)).place(x=330, y=y1 + 20)
        # FE1 &FE0 causes motor to move in a - and + direction until the reference signal changes state.
        Button(root, fg="black", width=3,
               text="-<<", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("FE0", address=1)).place(x=210, y=y1 + 20)

        Button(root, fg="black", width=3,
               text=">>+", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("FE1", address=1)).place(x=290, y=y1 + 20)

        # MA0 Moves motor to zero position
        Button(root, padx=4, bd=1, fg="Red", font=Font(family='times', size=9),
               text="Reset", command=lambda: dut["MotorStage"]._write_command("MA0", address=1)).place(x=245, y=y1 + 20)

        lblInfo = Label(root, padx=8, font=Font(family='times', size=10),
                        text="B", fg="Black", anchor='w').place(x=10, y=y2 + 20)

        e2 = DoubleVar()  # Relative Distance variable
        spinB = Spinbox(root, from_=-1073741824, to=1073741823, increment=1000, format="%0.2f",
                        textvariable=e2, width=10, font=Font(family='times', size=10))
        spinB.place(x=40, y=y2)
        MR2 = Button(root, fg="black", width=11,
                     text="Rel. Step >>", font=Font(family='times', size=9),
                     command=lambda: dut["MotorStage"].Read_Write("MR%d" % e2.get(), address=2)).place(x=40, y=y2 + 20)
        value_MA2 = Entry(root, width=11)
        value_MA2.place(x=130, y=y2)
        Button(root, fg="black", width=9,
               text="Go To >>", font=Font(family='times', size=11),
               command=lambda: dut["MotorStage"].Read_Write("MA%d" % int(re.search(r'\d+', value_MA2.get()).group()), address=2)).place(x=130, y=y2 + 20)

        # AB1 Stops the motor smoothly with programmed deceleration ramp. (Another command (AB) can be used to make a sudden stop for the motor)
        Button(root, fg="black", width=4,
               text="Abort", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("AB1", address=2)).place(x=330, y=y2 + 20)
        # FE1 &FE0 causes motor to move in a - and + direction until the reference signal changes state.
        Button(root, fg="black", width=3,
               text="-<<", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("FE0", address=2)).place(x=210, y=y2 + 20)
        Button(root, fg="black", width=3,
               text=">>+", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("FE1", address=2)).place(x=290, y=y2 + 20)

        Button(root, padx=4, bd=1, fg="Red", font=Font(family='times', size=9),
               text="Reset", command=lambda: dut["MotorStage"]._write_command("MA0", address=2)).place(x=245, y=y2 + 20)

        lblInfo = Label(root, padx=8, font=Font(family='times', size=10),
                        text="C", fg="Black", anchor='w').place(x=10, y=y3)
        e3 = DoubleVar()  # Relative Distance variable
        spinC = Spinbox(root, from_=-1073741824, to=1073741824, increment=1000, format="%0.2f",
                        textvariable=e3, width=10, font=Font(family='times', size=10))
        spinC.place(x=40, y=y3 + 5)
        Button(root, fg="black", width=11,
               text="Rel. Step >>", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"].Read_Write("MR%d" % e3.get(), address=3)).place(x=40, y=y3 + 20)

        value_MA3 = Entry(root, width=11)
        value_MA3.place(x=130, y=y3)
        Button(root, fg="black", width=9,
               text="Go To >>", font=Font(family='times', size=11),
               command=lambda: dut["MotorStage"].Read_Write("MA%d" % int(re.search(r'\d+', value_MA3.get()).group()), address=3)).place(x=130, y=y3 + 20)

        # AB1 Stops the motor smoothly with programmed deceleration ramp. (Another command (AB) can be used to make a sudden stop for the motor)
        Button(root, fg="black", width=4,
               text="Abort", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("AB1", address=3)).place(x=330, y=y3 + 20)
        # FE1 &FE0 causes motor to move in a - and + direction until the reference signal changes state.
        Button(root, fg="black", width=3,
               text="-<<", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("FE0", address=3)).place(x=210, y=y3 + 20)
        Button(root, fg="black", width=3,
               text=">>+", font=Font(family='times', size=9),
               command=lambda: dut["MotorStage"]._write_command("FE1", address=3)).place(x=290, y=y3 + 20)

        Button(root, padx=4, bd=1, fg="Red", font=Font(family='times', size=9),
               text="Reset", command=lambda: dut["MotorStage"].Read_Write("MA0", address=3)).place(x=245, y=y3 + 20)
        Button(root, text="Exit", bg='red', command=sys.exit).place(x=400, y=y3 + 60)
        root.mainloop()

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


if __name__ == '__main__':

    scan = Class()
    # scan.Restore_intial_positions()
    #scan.Calibration()
    #scan.Plan(Size_x=20000, Steps=442, width=20, Sourcemeter=True, Motor_Delay=2)
    scan.Plan2(Size_x=20000, Steps=150, width=50, Sourcemeter=True, Motor_Delay=2)
