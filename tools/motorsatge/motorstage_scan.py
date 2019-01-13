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
    #dut["ms"]._write_command("FE2", address=2)
    #dut["ms"]._write_command("FE2", address=3)
    # Restore intial positions
    # dut["MotorStage"].Read_Write("MR%d" % Limit, address=1)   # y Move to the Border (In-Out)
    # dut["MotorStage"].Read_Write("MR%d" % Limit, address=2)   # z Move to the Border (Up-Down)
    # dut["MotorStage"].Read_Write("MR%d" % -Limit, address=3)   # x Move to the Border (Left-Right)
    # Check Stages
    # dut["MotorStage"].Read_Write("MR 500000", address=1)  # y
    # dut["MotorStage"].Read_Write("MA3000000", address=1)  # x   (Move to the Middle)
    
def GUI_scan():
    dut = Dut('motorstage_Pyserial.yaml')
    dut.init()
    dut["ms"].GUI(root=Tk())  # x(in-out)
'''
Step1: Restore the intial position with Auto-Referencing Option: With standard PI stages
step2: show GUI to control the motor stage 
A: address=1
B: address=2
C: address=3

'''
#Restore_intial_positions()

GUI_scan()
