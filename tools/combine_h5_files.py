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


def combine_h5(Directory =None, file1=None, file2=None):
    with tb.open_file(Directory + file1, 'r') as in_file:
        beamspot_1 = in_file.root.beamspot[:]
        
    with tb.open_file(Directory + file2, 'r') as in_file:
        beamspot_2 = in_file.root.beamspot[:]       
    beamspot = np.zeros(shape=(beamspot_1.shape[0]+beamspot_2.shape[0]-1, beamspot_1.shape[1]), dtype=np.float64)
    for i in np.arange(beamspot_1.shape[0]+beamspot_2.shape[0]-1):
        for j in np.arange(beamspot_1.shape[1]):
            if i <=59:
               beamspot[i,j] =  beamspot_1[i,j]
            if i > 59:
               beamspot[i,j] =  beamspot_2[i-59,j]   
    plt.imshow(beamspot, aspect='auto', origin='upper')
    plt.show()
    with tb.open_file(Directory + "beamspot_combined_10cm.h5", "w") as out_file_h5:
        out_file_h5.create_array(out_file_h5.root, 'beamspot', beamspot, "beamspot")  
        
Directory = "/home/silab62/git/XrayMachine_Bonn/tools/motorsatge/"
combine_h5(Directory=Directory,file1="beamspot0_60_10cm.h5",file2="beamspot60_90_10cm.h5")