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

def temprature_dose(Directory=False, Sourcemeter=False,time_size=10,delay=10, CurrentLimit=1.000000E-06):
    '''
    Assuming that the cabinet door is the -z
    x : Number of movements to x direction 
    z: Number of movements inside the cabinet
    Size_x: size of the steps in x direction
    '''
    t0 = time.time()
    if Sourcemeter:
        dut = Dut('sensor_sourcemeter_scan_pyserial.yaml')
        dut.init()
        dut['ts'].write(":OUTP ON")
        dut['ts'].write("*RST")
        dut['ts'].write(":SOUR:VOLT:RANG 60")
        dut['ts'].write('SENS:CURR:PROT ' + str(CurrentLimit))
        print "The Protection Current limit is", dut['ts'].ask("SENS:CURR:PROT?")
        dut['ts'].write(":SOUR:FUNC VOLT")
        dut['ts'].write(':SOUR:VOLT 50')
        val = dut['ms'].ask(":MEAS:CURR?")
        current = val[15:-43]
    else:
        dut = Dut('temprature_scan_pyserial.yaml')
        dut.init()
        current = random.randint(1, 101)
    with tb.open_file(Directory +'temprature_dose.h5', "w") as out_file_h5:
        description = np.zeros((1,), dtype=np.dtype([("time", "f8"), ("temprature", "f8"),("humidity", "f8"), ("dew", "f8")])).dtype
        Data_table = out_file_h5.create_table(out_file_h5.root, name='temprature_dose',
                                                      description=description,
                                                      filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
        read = Data_table.row
            
        for i in xrange(time_size):
            t1 = time.time() 
            read["time"] = t1 -t0
            read["temprature"] =dut['ts'].get_temperature()
            read["humidity"] = dut['ts'].get_humidity()
            read["dew"] = dut['ts'].get_dew_point()
            read.append()                            
            print dut['ts'].get_temperature() , t1 -t0
            time.sleep(delay)
        Data_table.flush()
    out_file_h5.close()
'''
Step1: Restore the intial position with Auto-Referencing Option: With standard PI stages
step2: show GUI to control the motor stage 
'''
Directory = "/home/silab62/git/XrayMachine_Bonn/tools/temprature_sensor/"
temprature_dose(Directory=Directory)
#scan.Plan(Size_x=20000, Steps=442, width=20, Sourcemeter=True, Motor_Delay=2)
#scan.Plan2(Size_x=20000, Steps=150, width=50, Sourcemeter=True, Motor_Delay=2)
